
import json

from math import floor
from urllib import urlencode

from django.conf import settings
from django.contrib.auth import logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import Context

from petition.models import Signature

from icekey.utils import authenticate

def get_user_signatures(request):

    empty_response = False
    response = []
    total_signatures = 0

    if request.user.is_authenticated():

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

        signatures = Signature.objects.select_related('petition__name').filter(user=request.user).order_by('-date_created')
        print signatures

        try:
            p = Paginator(signatures, page_length)
            results = p.page(page_num)
        except PageNotAnInteger:
            results = p.page(1)
        except EmptyPage:
            results = p.page(paginator.num_pages)

        for s in results:
            o = []
            o.append(s.petition.name.capitalize())
            o.append(s.date_created.strftime("%Y-%m-%d %H:%M:%S"))

            response.append(o)

        total_signatures = p.count

    response_wrapper = {}
    response_wrapper['iTotalRecords'] = total_signatures
    response_wrapper['iTotalDisplayRecords'] = total_signatures
    response_wrapper['aaData'] = response

    return HttpResponse(json.dumps(response_wrapper), content_type="application/json")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def my_page(request):
    c = {}

    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    context = Context({
        'signatures_url': settings.INSTANCE_URL + reverse('get_user_signatures') + '',
        'page_title': 'My Page'
    })

    return render(request, 'person/my_page.html', context)


def signature_change_public(request, signature_id):
    if not request.user.is_authenticated():
        return HttpResponseForbidden()

    s = get_object_or_404(Signature, id=signature_id, user=request.user)

    s.show_public = not s.show_public
    s.save()

    return HttpResponseRedirect(reverse('signatures'))


def remove_signature(request, signature_id):

    if not request.user.is_authenticated():
        return HttpResponseForbidden()

    s = get_object_or_404(Signature, id=signature_id, user=request.user)

    redirect_to = request.GET.get('next', reverse('signatures'))

    if request.GET.get('answer', '').lower() == 'yes':
        s.delete()
        return HttpResponseRedirect(redirect_to)

    context = Context({
        'signature': s,
        'next': redirect_to,
    })

    if request.GET.get('method', '').lower() == 'browser-confirm':
        return render(request, 'person/remove_signature__json.html', context, content_type='application/json')
    else:
        return render(request, 'person/remove_signature.html', context)


def login_view(request):

    params = {'path': reverse('login')}
    auth_url = settings.AUTH_URL % urlencode(params)
    ret = authenticate(request, auth_url)
    if isinstance(ret, HttpResponse):
        return ret

    return HttpResponseRedirect(reverse('popular', current_app='petition'))


def test_auth(request):
    c = {}

    if request.method == 'POST':

        c['result'] = 'success'
        c['token'] = 'TestToken123'

        ret_url = request.GET.get('next')
        return HttpResponseRedirect(ret_url)

    return render_to_response('person/test_auth.html', c)
