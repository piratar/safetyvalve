
import urllib

from datetime import datetime
from lxml import etree
from pprint import pprint
from suds.client import Client
from StringIO import StringIO
from urllib import urlencode

from django.db.models import Count
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import Context

from petition.models import Petition
from person.models import UserAuthentication

from models import Signature


def index(request):
    p = Petition.objects.all().order_by('-date_created').annotate(num_signatures=Count('signature'))[:5]

    for i in p:
        if isinstance(i.name, unicode):
            i.name = i.name.encode('utf-8')

        url = urllib.quote("%s/petition/%s" % (settings.INSTANCE_URL, str(i.id)))

        #facebook share logic
        i.url_facebook_share = 'http://www.facebook.com/sharer/sharer.php?u=%s' % url

        #twitter length logic
        url_twitter_share = ('%s %s' % (url, i.name))
        url_twitter_share = url_twitter_share if len(url_twitter_share) <= 140 else url_twitter_share[:137] + '...'
        i.url_twitter_share = 'http://twitter.com/home?status=' + urllib.quote(url_twitter_share)

        #g+ share logic
        i.url_googleplus_share = 'https://plus.google.com/share?url=%s' % url

    context = Context({'petitions': p, 'instance_url': settings.INSTANCE_URL})
    return render(request, 'index.html', context)


def detail(request, petition_id):
    p = Petition.objects.get(id=petition_id)
    context = Context({'petition': p})
    return render(request, 'detail.html', context)


def now():
    return datetime.now()


def get_saml(request, token):
    # Fetch SAML info
    AI = settings.AUTH_ISLAND
    client = Client(AI['wsdl'], username=AI['login'], password=AI['password'])
    ipaddr = request.META.get('REMOTE_ADDR')
    result = client.service.generateSAMLFromToken(token, ipaddr)

    if result['status']['message'] != 'Success':
        raise Exception('SAML error: %s' % result['status']['message'])

    return result


def parse_saml(saml):
    # Parse the SAML and retrieve user info
    tree = etree.parse(StringIO(saml))
    namespaces = {'saml': 'urn:oasis:names:tc:SAML:1.0:assertion'}
    name = tree.xpath('/saml:Assertion/saml:AttributeStatement/saml:Subject/saml:NameIdentifier[@NameQualifier="Full Name"]/text()', namespaces=namespaces)[0]
    kennitala = tree.xpath('/saml:Assertion/saml:AttributeStatement/saml:Attribute[@AttributeName="SSN"]/saml:AttributeValue/text()', namespaces=namespaces)[0]
    return name, kennitala


def ensure_user(request, name, kennitala):
    user = User.objects.get_or_create(username=kennitala)[0]
    if user.first_name == '':
        user.first_name = name
        user.save()

    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    return user


def authenticate(request, redirect_url):
    user = request.user
    token = request.GET.get('token')

    auth_fake = getattr(settings, 'AUTH_FAKE', None)
    if auth_fake:
        if not token:
            curr_url = request.get_full_path().split('?')[0]
            return HttpResponseRedirect('%s?token=%s' % (curr_url, auth_fake['token']))
        name = auth_fake['name']
        kennitala = auth_fake['kennitala']

    if not token:
        return HttpResponseRedirect(redirect_url)

    if auth_fake is None:
        result = get_saml(request, token)
        name, kennitala = parse_saml(result['saml'])

    if not user.is_authenticated() or user.username != kennitala:
        user = ensure_user(request, name, kennitala)

    return user, token


def sign(request, petition_id):

    p = get_object_or_404(Petition, pk=petition_id)

    params = {'path': reverse('sign', args=(petition_id, ))[1:]}
    redirect_url = settings.AUTH_URL % urlencode(params)
    ret = authenticate(request, redirect_url)
    if isinstance(ret, HttpResponse):
        return ret
    else:
        user, token = ret

    auth = UserAuthentication()
    auth.user = user
    auth.token = token
    auth.generated = datetime.now()
    auth.method = 'icekey'
    auth.save()

    if Signature.objects.filter(user=user, petition=p).count():
        Signature.objects.filter(user=user, petition=p).delete()
    s = Signature(user=user, petition=p, authentication=auth)
    s.save()

    return HttpResponseRedirect(reverse('detail', args=(petition_id, )))
