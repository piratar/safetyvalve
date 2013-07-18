
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render_to_response

from petition.models import Signature


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def signatures(request):
    c = {}

    signs = Signature.objects.filter(user=request.user).order_by('-last_updated')

    c['signatures'] = signs

    return render_to_response(request, 'petition/signatures.html', c)

