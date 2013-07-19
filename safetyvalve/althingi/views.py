from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from BeautifulSoup import BeautifulSoup, Tag

import urllib

def home(request):

    url = 'http://www.althingi.is/altext/142/s/0014.html'

    content = urllib.urlopen(url).read().decode('ISO-8859-1')

    content = content.replace('&nbsp;', ' ')

    soup = BeautifulSoup(content)

    # Remove garbage.
    [s.extract() for s in soup('script')]
    [s.extract() for s in soup('noscript')]
    [s.extract() for s in soup('head')]
    [s.extract() for s in soup('small')]
    [s.extract() for s in soup('hr')]

    # Replace 'html' and 'body' tags'
    body_tag = soup.find('body')
    body_tag.attrs.append(('id', 'body_tag'))
    body_tag.name = 'div'
    html_tag = soup.find('html')
    html_tag.attrs.append(('id', 'html_tag'))
    html_tag.name = 'div'
    content = soup

    #return HttpResponse(content, content_type='text/plain')
    return HttpResponse(content, content_type='text/xml')

    #return render_to_response('althingi/home.html', { 'data': 'Some Data!' }, context_instance = RequestContext(request))

