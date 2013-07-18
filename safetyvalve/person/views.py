
from django.contrib.auth import logout
from django.shortcuts import HttpResponseRedirect


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

