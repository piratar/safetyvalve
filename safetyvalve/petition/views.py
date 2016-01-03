# -*- coding: utf-8 -*-

import codecs
import os
import json
import base64

from math import floor
from datetime import datetime, timedelta
from urllib.parse import urlencode, quote_plus, unquote_plus

from django import forms
from django.db.models import Count, Q
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import Context
from django.utils.translation import ugettext

from althingi.althingi_settings import CURRENT_SESSION_NUM

from safetyvalve.mail import create_email

from petition.models import Petition

from icekey.utils import authenticate

from .models import Signature
from .utils import convert_petition_to_plaintext_email

def all(request):

    petitions = Petition.objects.filter(external_id__startswith='%s.' % CURRENT_SESSION_NUM).order_by('-time_published')

    return index(request, 'All Issues', petitions)


def cached_or_function(key, fun, timeout=60 * 5, *args, **kwargs):
    x = cache.get(key)

    if x is None:
        item = fun(*args, **kwargs)
        cache.set(key, (item, datetime.now()), timeout)
        return item

    return x[0]


def detail(request, petition_id):

    petition = get_object_or_404(Petition, id=petition_id)

    stance = ''
    if request.user.is_authenticated():
        user_signatures = Signature.objects.filter(user=request.user, petition=petition)
        if len(user_signatures) == 1: # Should never be anything but 0 or 1
            stance = user_signatures[0].stance

    oppose_petition = Petition.objects.filter(id=petition_id, signature__stance='oppose').annotate(oppose_count=Count('signature'))
    if oppose_petition.count() > 0:
        petition.oppose_count = oppose_petition[0].oppose_count
    else:
        petition.oppose_count = 0

    endorse_petition = Petition.objects.filter(id=petition_id, signature__stance='endorse').annotate(endorse_count=Count('signature'))
    if endorse_petition.count() > 0:
        petition.endorse_count = endorse_petition[0].endorse_count
    else:
        petition.endorse_count = 0

    petition.total_count = petition.oppose_count + petition.endorse_count

    context = Context({
        'p': petition,
        'stance': stance,
        'signatures_url': reverse('get_public_signatures', args=(petition_id, )) + '' ,
        'INSTANCE_URL' : settings.INSTANCE_URL
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
        signature = {}
        signature = {'signature_stance': s.stance,
                     'signature_name': '%s %s' % (s.user.first_name, s.user.last_name) if s.show_public else ugettext('[ Name hidden ]')}
        o.append(signature)
        o.append(s.user.username if s.show_public else ugettext('[ SSN hidden ]'))
        o.append(s.date_created.strftime("%Y-%m-%d %H:%M:%S"))

        response.append(o)

    response_wrapper = {}
    response_wrapper['iTotalRecords'] = p.count
    response_wrapper['iTotalDisplayRecords'] = p.count
    response_wrapper['aaData'] = response


    return HttpResponse(json.dumps(response_wrapper), content_type="application/json")

def index(request, page_title, petitions, search_terms=""):

    # p = cached_or_function('popular__petitions', get_petitions, 60 * 5)

    if request.META['SERVER_NAME'] in settings.FAKE_AUTH_URLS and hasattr(settings, 'FAKE_AUTH'):
        if request.GET.get('fake-auth'):
            request.session['fake_auth'] = request.GET.get('fake-auth', '').lower() == 'on'


    paginator = Paginator(petitions, settings.INDEX_PAGE_ITEMS)

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

    if request.META['SERVER_NAME'] in settings.FAKE_AUTH_URLS and hasattr(settings, 'FAKE_AUTH'):
        if request.GET.get('fake-auth'):
            request.session['fake_auth'] = request.GET.get('fake-auth', '').lower() == 'on'

    # Seems like this should be taken care of at an earlier stage. -helgi@binary.is, 2014-05-19
    for i in petitions:
        if isinstance(i.name, str):
            i.name = i.name.encode('utf-8')


    total_pages = paginator.num_pages

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


    # Counting stances: First, we get a list of the IDs of petitions we actually need info on
    id_list = [p.id for p in petitions.object_list] # Paginator has turns QuerySet into list at this point

    # Counting stances: We check the number of the 'oppose' stances
    oppose_counts_query = Petition.objects.filter(id__in=id_list, signature__stance='oppose').annotate(oppose_count=Count('signature'))
    oppose_counts = {}
    for p in oppose_counts_query:
        oppose_counts[p.id] = p.oppose_count

    # Counting stances: We check the count of the 'endorse' stance as well
    endorse_counts_query = Petition.objects.filter(id__in=id_list, signature__stance='endorse').annotate(endorse_count=Count('signature'))
    endorse_counts = {}
    for p in endorse_counts_query:
        endorse_counts[p.id] = p.endorse_count

    # Counting stances: We write the values in places available to the template engine
    for p in petitions:
        if p.id in oppose_counts:
            p.oppose_count = oppose_counts[p.id]
        else:
            p.oppose_count = 0

        if p.id in endorse_counts:
            p.endorse_count = endorse_counts[p.id]
        else:
            p.endorse_count = 0

        issue_number = p.external_id.split('.')
        if(len(issue_number) > 1):
            issue_number = issue_number[1] + '/' + issue_number[0]
        else:
            issue_number = "blah"

        p.issue_number = issue_number

        p.total_count = p.oppose_count + p.endorse_count


    # Having separate lists for 'oppose' and 'support' was honestly the tidiest solution that
    # I found for displaying to the user his previous action.. - Django templates basically
    # just don't support looking up dict elements. Considered using Jinja instead of the
    # Django template engine but decided not to. -helgi@binary.is, 2014-05-19
    oppose_petition_ids = []
    endorse_petition_ids = []
    if request.user.is_authenticated():
        signatures = Signature.objects.filter(user=request.user)
        oppose_petition_ids = [s.petition_id for s in signatures if s.stance == 'oppose']
        endorse_petition_ids = [s.petition_id for s in signatures if s.stance == 'endorse']

    context = Context({
        'petitions': petitions,
        'instance_url': settings.INSTANCE_URL,
        'oppose_petition_ids': oppose_petition_ids,
        'endorse_petition_ids': endorse_petition_ids,
        'pages' : pages,
        'current_page': page,
        'page_title': page_title,
        'INSTANCE_URL': settings.INSTANCE_URL,
        'search_terms': search_terms
    })

    return render(request, 'index.html', context)


def popular(request):

    def get_popular_petitions():
        time_limit = datetime.now() - timedelta(days=3)
        return Petition.objects.annotate(num_signatures=Count('signature')).filter(
            Q(num_signatures__gte=settings.POPULAR_SIGNATURE_THRESHOLD) | Q(time_published__gt=time_limit),
            external_id__startswith=CURRENT_SESSION_NUM
        ).order_by('-num_signatures', '-time_published')
    #petitions = cached_or_function('popular__petitions', get_popular_petitions, settings.PETITION_LIST_CACHE_TIMEOUT)
    petitions = get_popular_petitions()


    return index(request, 'Hottest', petitions)


def search_terms(request):
    c = {}

    class SearchForm(forms.Form):
        search_terms = forms.CharField(label=ugettext('Search Terms'), required=False)

        def clean(self):
            if (self.cleaned_data.get('search_terms') == '' or self.cleaned_data.get('search_terms') == ' '):
                raise forms.ValidationError(
                    ugettext("You must enter a search term")
                )
            return self.cleaned_data

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            clean_search_terms = form.cleaned_data['search_terms']
            return HttpResponseRedirect(reverse('search_results', args=(quote_plus(clean_search_terms.encode("utf-8")), )))
    else:
        form = SearchForm()

    c['form'] = form
    c['page_title'] = 'Search'

    return render(request, 'petition/search_terms.html', c)


def search_results(request, search_terms):

    clean_search_terms = unquote_plus(search_terms.encode("utf-8"))

    petitions = Petition.objects.search(clean_search_terms)

    return index(request, 'Search Results', petitions, clean_search_terms)



def sign(request, petition_id, stance):

    p = get_object_or_404(Petition, pk=petition_id)

    show_public = int(request.GET.get('show_public', 0))

    params = {'path': reverse('sign', args=(petition_id, stance)) + '?show_public=%d' % show_public}
    auth_url = settings.AUTH_URL % urlencode(params)
    ret = authenticate(request, auth_url)
    if isinstance(ret, HttpResponse):
        return ret
    else:
        auth = ret

    if Signature.objects.filter(user=auth.user, petition=p).count():
        Signature.objects.filter(user=auth.user, petition=p).delete()
    s = Signature(user=auth.user, petition=p, show_public=show_public, authentication=auth, stance=stance)
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
    sender = settings.INSTANCE_NOREPLY_EMAIL
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

    subject = u'Staðfesting undirskriftar á Ventill.is - ' + s.petition.name

    template = 'email/sign_notification.%s.txt' % s.stance
    template_path = os.path.join(settings.TEMPLATE_DIRS[0], template)
    message = codecs.open(template_path, 'r', 'utf-8').read()
    message = message % {
        'name': request.user.first_name,
        'token': s.authentication.token,
        'subject': subject.replace,
        'title': s.petition.name,
        'text': convert_petition_to_plaintext_email(s.petition.content),
        'detail_url': settings.INSTANCE_URL + reverse('detail', args=(petition_id, ))
        }

    template = 'email/sign_notification.%s.html' % s.stance
    template_path = os.path.join(settings.TEMPLATE_DIRS[0], template)
    html = codecs.open(template_path, 'r', 'utf-8').read()
    html = html % {
        'name': request.user.first_name,
        'token': s.authentication.token,
        'subject': subject,
        'title': s.petition.name,
        'text': s.petition.content,
        'detail_url': settings.INSTANCE_URL + reverse('detail', args=(petition_id, ))
        }

    ret = _receipt(request, petition_id, subject, message, html)

    if isinstance(ret, HttpResponseRedirect):
        s.mail_sent = True
        s.save()

    return ret


def unsign_receipt(request, petition_id):
    p = get_object_or_404(Petition, pk=petition_id)
    s = get_object_or_404(Signature, user=request.user, petition=p)

    subject = u'Staðfesting á fjarlægingu undirskriftar á Ventill.is - ' + s.petition.name

    template = 'email/unsign_notification.%s.txt' % s.stance
    template_path = os.path.join(settings.TEMPLATE_DIRS[0], template)
    message = codecs.open(template_path, 'r', 'utf-8').read()
    message = message % {
        'name': request.user.first_name,
        'token': s.authentication.token,
        'subject': subject,
        'title': s.petition.name,
        'text': convert_petition_to_plaintext_email(s.petition.content),
        'detail_url': settings.INSTANCE_URL + reverse('detail', args=(petition_id, ))
        }

    template = 'email/unsign_notification.%s.html' % s.stance
    template_path = os.path.join(settings.TEMPLATE_DIRS[0], template)
    html = codecs.open(template_path, 'r', 'utf-8').read()
    html = html % {
        'name': request.user.first_name,
        'token': s.authentication.token,
        'subject': subject,
        'title': s.petition.name,
        'text': s.petition.content,
        'detail_url': settings.INSTANCE_URL + reverse('detail', args=(petition_id, ))
        }

    ret = _receipt(request, petition_id, subject, message, html)

    #if isinstance(ret, HttpResponseRedirect):
    s.delete()

    return ret
