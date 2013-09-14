# -*- coding: utf-8 -*-

import codecs
import urllib

from urllib import urlencode

from django import forms
from django.db.models import Count
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import Context
from django.utils.translation import ugettext

from safetyvalve.mail import create_email

from petition.models import Petition

from icekey.utils import authenticate

from models import Signature


def index(request):
    p = Petition.objects.all().order_by('-date_created').annotate(num_signatures=Count('signature'))

    if request.META['SERVER_NAME'] not in ['www.ventill.is', 'ventill.is']:
        if request.GET.get('fake-auth'):
            request.session['fake_auth'] = request.GET.get('fake-auth', '').lower() in ['on', 'true']

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

    signed_petition_ids = []
    if request.user.is_authenticated():
        signs = Signature.objects.filter(user=request.user)
        signed_petition_ids = [s.petition_id for s in signs]

    context = Context({
        'petitions': p,
        'instance_url': settings.INSTANCE_URL,
        'signed_petition_ids': signed_petition_ids
    })

    return render(request, 'index.html', context)


def detail(request, petition_id):
    p = Petition.objects.get(id=petition_id)

    already_signed = False
    if request.user.is_authenticated():
        already_signed = Signature.objects.filter(user=request.user, petition=p).count() > 0

    signatures = Signature.objects.select_related('user').filter(petition_id=petition_id).order_by('date_created')

    context = Context({
        'petition': p,
        'signatures': signatures,
        'already_signed': already_signed
    })

    return render(request, 'detail.html', context)


def sign(request, petition_id):

    p = get_object_or_404(Petition, pk=petition_id)

    show_public = int(request.GET.get('show_public', 0))

    params = {'path': reverse('sign', args=(petition_id, )) + '?show_public=%d' % show_public}
    auth_url = settings.AUTH_URL % urlencode(params)
    ret = authenticate(request, auth_url)
    if isinstance(ret, HttpResponse):
        return ret
    else:
        auth = ret

    if Signature.objects.filter(user=auth.user, petition=p).count():
        Signature.objects.filter(user=auth.user, petition=p).delete()
    s = Signature(user=auth.user, petition=p, show_public=show_public, authentication=auth)
    s.save()

    if not request.user.email:
        return HttpResponseRedirect(reverse('email', args=(petition_id, )))

    return HttpResponseRedirect(reverse('sign_receipt', args=(petition_id, )))


def unsign(request, petition_id):

    p = get_object_or_404(Petition, pk=petition_id)
    s = get_object_or_404(Signature, user=request.user, petition=p)

    if request.user.email:
        ret = unsign_receipt(request, petition_id)
        if not isinstance(ret, HttpResponseRedirect):
            return ret
    else:
        s.delete()
    return HttpResponseRedirect('/')


def email(request, petition_id):
    c = {}

    class EmailForm(forms.Form):
        email = forms.EmailField(label=ugettext('Email address'))
        confirm_email = forms.EmailField(label=ugettext('Confirm email address'))

        def clean(self):
            if (self.cleaned_data.get('email') !=
                self.cleaned_data.get('confirm_email')):
                raise forms.ValidationError(
                    ugettext("Email addresses must match")
                )
            return self.cleaned_data

    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            request.user.email = form.cleaned_data['email']
            request.user.save()
            return HttpResponseRedirect(reverse('sign_receipt', args=(petition_id, )))
    else:
        form = EmailForm()

    c['form'] = form

    return render(request, 'petition/email.html', c)


def _receipt(request, petition_id, subject, message, html=None):
    sender = 'stadfesting@ventill.is'
    recipients = [request.user.email]

    try:
        email = create_email(subject, message, html, from_email=sender)
        email.to = recipients
        email.send()

    except Exception as e:
        c = {'e': e}
        return render(request, 'petition/receipt_error.html', c)

    return HttpResponseRedirect(reverse('detail', args=(petition_id, )))


def sign_receipt(request, petition_id):
    p = get_object_or_404(Petition, pk=petition_id)
    s = get_object_or_404(Signature, user=request.user, petition=p)

    subject = u'Staðfesting undirskriftar á Ventill.is'

    message = codecs.open('templates/email/sign_notification.txt', 'r', 'utf-8').read()
    message = message % {
        'name': request.user.first_name,
        'token': s.authentication.token,
        'subject': subject,
        'text': s.petition.content,
        }

    html = codecs.open('templates/email/sign_notification.html', 'r', 'utf-8').read()
    html = html % {
        'name': request.user.first_name,
        'token': s.authentication.token,
        'subject': subject,
        'text': s.petition.content,
        }

    ret = _receipt(request, petition_id, subject, message, html)

    if isinstance(ret, HttpResponseRedirect):
        s.mail_sent = True
        s.save()

    return ret


def unsign_receipt(request, petition_id):
    p = get_object_or_404(Petition, pk=petition_id)
    s = get_object_or_404(Signature, user=request.user, petition=p)

    subject = u'Staðfesting á fjarlægingu undirskriftar á Ventill.is'

    message = codecs.open('templates/email/unsign_notification.txt', 'r', 'utf-8').read()
    message = message % {
        'name': request.user.first_name,
        'token': s.authentication.token,
        'subject': subject,
        'text': s.petition.content,
        }

    html = codecs.open('templates/email/unsign_notification.html', 'r', 'utf-8').read()
    html = html % {
        'name': request.user.first_name,
        'token': s.authentication.token,
        'subject': subject,
        'text': s.petition.content,
        }

    ret = _receipt(request, petition_id, subject, message, html)

    if isinstance(ret, HttpResponseRedirect):
        s.delete()

    return ret
