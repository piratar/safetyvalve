
from django.conf.urls import patterns, url


urlpatterns = patterns('person.views',
    url(r'^innskra/$', 'login_view', name='login'),
    url(r'^utskra/$', 'logout_view', name='logout'),
    url(r'^undirskriftir/$', 'signatures', name='signatures'),
    url(r'^undirskriftir/fjarlaegja/(?P<signature_id>\d+)/$', 'remove_signature', name='remove_signature'),
    url(r'^undirskriftir/breyta-opinber/(?P<signature_id>\d+)/$', 'signature_change_public'),
)
