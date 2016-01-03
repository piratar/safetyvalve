
import os
import binascii
from lxml import etree
from io import StringIO

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from suds.client import Client

from core.views import authentication_error
from person.models import UserAuthentication


def get_saml(request, token):
    # Fetch SAML info
    AI = settings.AUTH_ISLAND
    result = None

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
        user.first_name = name.encode('utf8')
        user.save()

    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    return user


def authenticate(request, redirect_url):
    user = request.user
    token = request.GET.get('token')

    if request.session.get('fake_auth') and request.META['SERVER_NAME'] in settings.FAKE_AUTH_URLS and hasattr(settings, 'FAKE_AUTH'):
        fake_auth = settings.FAKE_AUTH
        if not token:
            curr_url = request.get_full_path().split('?')[0]
            fake_token = binascii.b2a_hex(os.urandom(10))
            return HttpResponseRedirect('%s?show_public=%s&token=%s' % (curr_url, str(request.GET.get('show_public', 0)), fake_token))

        name = fake_auth['name']
        kennitala = fake_auth['kennitala']
    else:
        fake_auth = None

    if not token:
        return HttpResponseRedirect(redirect_url)

    if fake_auth is None:

        result = get_saml(request, token)
        name, kennitala = parse_saml(result['saml'])
        '''
        # If the WebFault exception is still popping up (yet to be determined), this should be
        # moved to an exception-handling middleware of some sorts. For now, we will let the
        # exception be raised at this point and handled by the 500-error handling mechanism.
        #
        # Remove this section if 2014-11-02 was a very long time ago, but please remember to then
        # also remove the "authentication_error" view in 'core.views.py'.
        try:
            result = get_saml(request, token)
            name, kennitala = parse_saml(result['saml'])
        except Exception as ex:
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print message
            
            return authentication_error(request, '')
        '''

    if not user.is_authenticated() or user.username != kennitala:
        user = ensure_user(request, name, kennitala)

    auth = UserAuthentication()
    auth.user = user
    auth.token = token
    auth.method = 'icekey'
    auth.save()

    return auth
