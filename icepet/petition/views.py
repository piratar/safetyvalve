from django.http import HttpResponse
from django.template import Context
from django.shortcuts import render

from petition.models import Petition

def index(request):
    context = {}
    return render(request, 'base.html', context)

def detail(request, petition_id):
    p = Petition.objects.get(id=petition_id)
    context = Context({'petition': p})
    return render(request, 'detail.html', context)