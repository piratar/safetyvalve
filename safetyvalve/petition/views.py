
from datetime import datetime
from pprint import pprint
from pysimplesoap.client import SoapClient
from urllib import urlencode
import urllib

from django.db.models import Count, Q
from django.conf import settings
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


def sign(request, petition_id):
    c = {}

    p = get_object_or_404(Petition, pk=petition_id)

    user = request.user
    if user.is_authenticated():
        auths = UserAuthentication.objects.filter(Q(expires=None) | Q(expires__gt=now()), user=user, petition=p)
    else:
        auths = []

    if not auths:

        token = request.GET.get('token')

        if not token:

            params = {'path': reverse('sign', args=(petition_id, ))[1:]}
            return HttpResponseRedirect(settings.AUTH_URL % urlencode(params))

        else:

            # Fetch SAML info
            import base64

            AI = settings.AUTH_ISLAND
            encoded = base64.encodestring('%s:%s' % (AI['login'], AI['password']))
            headers = {'Authorization': 'Basic %s' % encoded}

            client = SoapClient(wsdl=AI['wsdl'], trace=False, http_headers=headers)

            ipaddr = request.META.get('REMOTE_ADDR')
#            ipaddr = '81.15.30.31'

            result = client.generateSAMLFromToken(token, ipaddr)

#            result_example = {
#                'status': {
#                    'message': 'Success',
#                    'code': '',
#                    'type': '',
#                    #...
#                },
#                'saml': '<hello>SamlInfo</hello>',
#            }

            pprint(result['saml'])
            saml = {
                'kennitala': '1234',
            }

            if not user.is_authenticated():
                user = User()
                user.username = saml['kennitala']

            auth = UserAuthentication()
            auth.user = user
            auth.petition = p
            auth.token = token
            auth.generated = datetime.now()
            auth.method = 'icekey'
            auth.save()


    s, created = Signature.objects.get_or_create(user=user, petition=p)

    return HttpResponse(str(s) + ' ' + str(created))
    return render(request, 'sign.html', c)


def authenticate(request):
    c = {}

    # Check if already has authentication

    return render(request, 'authenticate.html', c)
