
import urllib

from urllib import urlencode

from django.db.models import Count
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import Context

from petition.models import Petition

from icekey.utils import authenticate

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


def sign(request, petition_id):

    p = get_object_or_404(Petition, pk=petition_id)

    params = {'path': reverse('sign', args=(petition_id, ))[1:]}
    redirect_url = settings.AUTH_URL % urlencode(params)
    ret = authenticate(request, redirect_url)
    if isinstance(ret, HttpResponse):
        return ret
    else:
        auth = ret

    if Signature.objects.filter(user=auth.user, petition=p).count():
        Signature.objects.filter(user=auth.user, petition=p).delete()
    s = Signature(user=auth.user, petition=p, authentication=auth)
    s.save()

    return HttpResponseRedirect(reverse('detail', args=(petition_id, )))
