# -*- coding: utf-8 -*-

import urllib

from urllib import urlencode

from django import forms
from django.db.models import Count
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import Context

from petition.models import Petition

from icekey.utils import authenticate

from models import Signature


def index(request):
    p = Petition.objects.all().order_by('-date_created').annotate(num_signatures=Count('signature'))

    for i in p:
        if isinstance(i.name, unicode):
            i.name = i.name.encode('utf-8')

        url = urllib.quote("%s/petition/%s" % (settings.INSTANCE_URL, str(i.id)))

        #facebook share logic
        i.url_facebook_share = 'http://www.facebook.com/sharer/sharer.php?u=%s' % url

        #twitter length logic
        url_twitter_share = ('%s %s' % (url, i.name))
        url_twitter_share = url_twitter_share if len(url_twitter_share) <= 140 else url_twitter_share[:137] + '...'
        i.url_twitter_share = 'http://twitter.com/home?status=' + urllib.quote(url_twitter_share)

        #g+ share logic
        i.url_googleplus_share = 'https://plus.google.com/share?url=%s' % url

    context = Context({'petitions': p, 'instance_url': settings.INSTANCE_URL})
    return render(request, 'index.html', context)


def detail(request, petition_id):
    p = Petition.objects.get(id=petition_id)

    context = Context({'petition': p})
    return render(request, 'detail.html', context)


def sign(request, petition_id):

    p = get_object_or_404(Petition, pk=petition_id)

    params = {'path': reverse('sign', args=(petition_id, ))[1:]}
    auth_url = settings.AUTH_URL % urlencode(params)
    ret = authenticate(request, auth_url)
    if isinstance(ret, HttpResponse):
        return ret
    else:
        auth = ret

    if Signature.objects.filter(user=auth.user, petition=p).count():
        Signature.objects.filter(user=auth.user, petition=p).delete()
    s = Signature(user=auth.user, petition=p, authentication=auth)
    s.save()

    if not request.user.email:
        return HttpResponseRedirect(reverse('email', args=(petition_id, )))

    return HttpResponseRedirect(reverse('receipt', args=(petition_id, )))


def email(request, petition_id):
    c = {}

    class EmailForm(forms.Form):
        email = forms.EmailField()
        confirm_email = forms.EmailField()

        def clean(self):
            if (self.cleaned_data.get('email') !=
                self.cleaned_data.get('confirm_email')):
                raise forms.ValidationError(
                    "Email addresses must match."
                )
            return self.cleaned_data

    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            request.user.email = form.cleaned_data['email']
            request.user.save()
            return HttpResponseRedirect(reverse('receipt', args=(petition_id, )))
    else:
        form = EmailForm()

    c['form'] = form

    return render(request, 'petition/email.html', c)


def receipt(request, petition_id):

    p = get_object_or_404(Petition, pk=petition_id)
    s = get_object_or_404(Signature, user=request.user, petition=p)

    subject = u'Staðfesting undirskriftar á Ventill.is'
    message = u'''Sæl(l) %s!

Takk fyrir að nota kerfið okkar. Hér með staðfestist að þú hafir skrifað undir eftirfarandi lög með tókanum %s frá island.is:

> %s

Með kveðju,
Ventill.is
''' % (request.user.first_name, s.authentication.token, s.petition.content.replace('\n', '\n> '))
    sender = 'stadfesting@ventill.is'
    recipients = [request.user.email]

    #send_mail(subject, message, sender, recipients)

    s.mail_sent = True
    s.save()

    return HttpResponseRedirect(reverse('detail', args=(petition_id, )))
