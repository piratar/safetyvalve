
from lxml import etree
from StringIO import StringIO
from suds.client import Client

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from person.models import UserAuthentication


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

    auth = UserAuthentication()
    auth.user = user
    auth.token = token
    auth.method = 'icekey'
    auth.save()

    return auth
