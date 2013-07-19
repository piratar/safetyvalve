from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from BeautifulSoup import BeautifulSoup

import urllib

def home(request):

    url = 'http://www.althingi.is/altext/142/s/0014.html'

    content = urllib.urlopen(url).read().decode('ISO-8859-1')

    content = content.replace('&nbsp;', ' ')

    soup = BeautifulSoup(content)
    content = soup.prettify()

    return HttpResponse(content, content_type='text/html')

    #return render_to_response('althingi/home.html', { 'data': 'Some Data!' }, context_instance = RequestContext(request))

