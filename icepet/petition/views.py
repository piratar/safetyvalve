from django.http import HttpResponse
from django.template import Context
from django.shortcuts import render

from petition.models import Petition

def index(request):
    p = Petition.objects.all().order_by('-date_created').annotate(num_signatures=Count('signature'))[:5]

    context = Context({'petitions':p})
    return render(request, 'index.html', context)

def detail(request, petition_id):
    p = Petition.objects.get(id=petition_id)
    context = Context({'petition': p})
    return render(request, 'detail.html', context)