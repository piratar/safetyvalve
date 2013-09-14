
from urllib import urlencode

from django.conf import settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.shortcuts import render, render_to_response, get_object_or_404
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

    signs = Signature.objects.filter(user=request.user).order_by('-date_created')

    c['signatures'] = signs

    return render(request, 'petition/signatures.html', Context(c))


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
