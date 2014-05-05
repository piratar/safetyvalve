# -*- coding: utf-8 -*-

import codecs
import os
import json

from math import floor
from datetime import datetime
from urllib import urlencode

from django import forms
from django.db.models import Count
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import Context
from django.utils.translation import ugettext

from safetyvalve.mail import create_email

from petition.models import Petition

from icekey.utils import authenticate

from models import Signature
from utils import convert_petition_to_plaintext_email


def cached_or_function(key, fun, timeout=60 * 5, *args, **kwargs):
    x = cache.get(key)
    if x is None:
        item = fun(*args, **kwargs)
        cache.set(key, (item, datetime.now()), timeout)
        return item
    return x[0]


def detail(request, petition_id):
    p = Petition.objects.get(id=petition_id)

    already_signed = False
    if request.user.is_authenticated():
        already_signed = Signature.objects.filter(user=request.user, petition=p).count() > 0

    signatures = Signature.objects.select_related('user').filter(petition_id=petition_id).order_by('date_created')


    context = Context({
        'petition': p,
        'signatures': signatures,
        'already_signed': already_signed,
        'signatures_url': settings.INSTANCE_URL + reverse('get_public_signatures', args=(petition_id, )) + ''  
    })

    return render(request, 'detail.html', context)


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


def get_public_signatures(request, petition_id):

    empty_response = False
    response = []

    start_index = int(request.GET.get('iDisplayStart', 0))
    page_length = int(request.GET.get('iDisplayLength', 0))

    if start_index < 0:
        start_index = 0;
    if page_length < 1:
        page_length = 1

    page_num = floor(start_index / page_length) + 1

    sort_index = int(request.GET.get('iSortCol_0', 0))
    sort_dir = request.GET.get('sSortDir_0', "desc")

    if sort_dir not in ["asc", "desc"]:
        sort_dir = "desc"

    if sort_index == 0:
        sort_fields = ['user__first_name', 'user__last_name']
    else:
        sort_fields = ['date_created']

    for i in xrange(len(sort_fields)):
        if sort_dir == "desc":
            sort_fields[i] = "-"+sort_fields[i]

    signatures = Signature.objects.select_related('user').filter(petition_id=petition_id).order_by(*sort_fields)
    try:
        p = Paginator(signatures, page_length)
        results = p.page(page_num)
    except PageNotAnInteger:
        results = p.page(1)
    except EmptyPage:
        results = p.page(paginator.num_pages)

    for s in results:
        o = []
        o.append(s.user.first_name + " " + s.user.last_name)
        o.append(s.user.username)
        o.append(s.date_created.strftime("%Y-%m-%d %H:%M:%S"))

        response.append(o)

    response_wrapper = {}
    response_wrapper['iTotalRecords'] = p.count
    response_wrapper['iTotalDisplayRecords'] = p.count
    response_wrapper['aaData'] = response


    return HttpResponse(json.dumps(response_wrapper), content_type="application/json")


def index(request):

    # def get_petitions():
    #     return Petition.objects.all() \
    #                            .order_by('-date_created') \
    #                            .annotate(num_signatures=Count('signature'))

    # p = cached_or_function('popular__petitions', get_petitions, 60 * 5)

    all_petitions = Petition.objects.all().order_by('-date_created').annotate(num_signatures=Count('signature'))
    paginator = Paginator(all_petitions, settings.INDEX_PAGE_ITEMS)

    page = request.GET.get('page', 1)
    try:
        petitions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page = 1
        petitions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page = 1
        petitions = paginator.page(1)

    page = int(page) #seems to come back as a unicode string in some occasions

    if request.META['SERVER_NAME'] not in ['www.ventill.is', 'ventill.is']:
        if request.GET.get('fake-auth'):
            request.session['fake_auth'] = request.GET.get('fake-auth', '').lower() in ['on', 'true']

    for i in petitions:
        if isinstance(i.name, unicode):
            i.name = i.name.encode('utf-8')

        if i.num_signatures > 999:
            i.num_signatures_display = '%.3gK' % (i.num_signatures / 1000)
        else:
            i.num_signatures_display = i.num_signatures


    total_pages = paginator.num_pages;

    if total_pages <= settings.PAGE_BUTTONS_THRESHOLD:
        pages = paginator.page_range
    else:
        pages_padded_start = page - settings.CURRENT_PAGE_BUTTON_PADDING

        if pages_padded_start <= 1:
            pages_padded_start = 2

        pages_padded_end = (settings.CURRENT_PAGE_BUTTON_PADDING * 2) + pages_padded_start + 1

        if pages_padded_end > total_pages:
            pages_padded_end = total_pages
            pages_padded_start = total_pages - (settings.CURRENT_PAGE_BUTTON_PADDING * 2 + 1)

        pages = [1]

        for i in range (pages_padded_start, pages_padded_end):
            pages.append(i);

        pages.append(total_pages)

        if page - settings.CURRENT_PAGE_BUTTON_PADDING > 1:
            pages.insert(1, '...')

        if page + settings.CURRENT_PAGE_BUTTON_PADDING < total_pages - 1:
            pages.insert(len(pages)-1, '...')


    signed_petition_ids = []
    if request.user.is_authenticated():
        signs = Signature.objects.filter(user=request.user)
        signed_petition_ids = [s.petition_id for s in signs]

    context = Context({
        'petitions': petitions,
        'instance_url': settings.INSTANCE_URL,
        'signed_petition_ids': signed_petition_ids,
        'pages' : pages,
        'current_page': page
    })

    return render(request, 'index.html', context)


def popular(request):

    def get_popular_petitions():
        return Petition.objects \
                       .annotate(num_signatures=Count('signature')) \
                       .filter(num_signatures__gt=0) \
                       .order_by('-num_signatures')[:10]
    petitions = cached_or_function('popular__petitions', get_popular_petitions, 10)

    context = Context({
        'petitions': petitions,
    })

    return render(request, 'petition/popular.html', context)


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

    template = 'email/sign_notification.txt'
    template_path = os.path.join(settings.TEMPLATE_DIRS[0], template)
    message = codecs.open(template_path, 'r', 'utf-8').read()
    message = message % {
        'name': request.user.first_name,
        'token': s.authentication.token,
        'subject': subject.replace,
        'title': s.petition.name,
        'text': convert_petition_to_plaintext_email(s.petition.content),
        }

    template = 'email/sign_notification.html'
    template_path = os.path.join(settings.TEMPLATE_DIRS[0], template)
    html = codecs.open(template_path, 'r', 'utf-8').read()
    html = html % {
        'name': request.user.first_name,
        'token': s.authentication.token,
        'subject': subject,
        'title': s.petition.name,
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

    template = 'email/unsign_notification.txt'
    template_path = os.path.join(settings.TEMPLATE_DIRS[0], template)
    message = codecs.open(template_path, 'r', 'utf-8').read()
    message = message % {
        'name': request.user.first_name,
        'token': s.authentication.token,
        'subject': subject,
        'title': s.petition.name,
        'text': convert_petition_to_plaintext_email(s.petition.content),
        }

    template = 'email/unsign_notification.html'
    template_path = os.path.join(settings.TEMPLATE_DIRS[0], template)
    html = codecs.open(template_path, 'r', 'utf-8').read()
    html = html % {
        'name': request.user.first_name,
        'token': s.authentication.token,
        'subject': subject,
        'title': s.petition.name,
        'text': s.petition.content,
        }

    ret = _receipt(request, petition_id, subject, message, html)

    if isinstance(ret, HttpResponseRedirect):
        s.delete()

    return ret
