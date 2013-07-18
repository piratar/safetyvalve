
from urllib import urlencode

from django.conf import settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template import Context

from petition.models import Signature

from icekey.utils import authenticate


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


def signatures(request):
    c = {}

    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    signs = Signature.objects.filter(user=request.user).order_by('-last_updated')

    c['signatures'] = signs

    return render(request, 'petition/signatures.html', Context(c))


def login_view(request):

    params = {'path': reverse('login')[1:]}
    auth_url = settings.AUTH_URL % urlencode(params)
    ret = authenticate(request, auth_url)
    if isinstance(ret, HttpResponse):
        return ret

    return HttpResponseRedirect(reverse('signatures'))


def test_auth(request):
    c = {}

    if request.method == 'POST':

        c['result'] = 'success'
        c['token'] = 'TestToken123'

        ret_url = request.GET.get('next')
        return HttpResponseRedirect(ret_url)

    return render_to_response('person/test_auth.html', c)
