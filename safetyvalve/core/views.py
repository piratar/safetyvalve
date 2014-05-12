
from django.shortcuts import render
from django.template import Context


def about_us(request):
    return render(request, 'about_us.html', Context({'page_title':'About Us'}))
