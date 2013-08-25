
from django.conf.urls import patterns, url


urlpatterns = patterns('person.views',
    url(r'^login/$', 'login_view', name='login'),
    url(r'^logout/$', 'logout_view', name='logout'),
    url(r'^signatures/$', 'signatures', name='signatures'),
    url(r'^signatures/remove/(?P<signature_id>\d+)/$', 'remove_signature', name='remove_signature'),
    url(r'^signatures/change-public/(?P<signature_id>\d+)/$', 'signature_change_public'),

    (r'^test_auth/$', 'test_auth'),
)
