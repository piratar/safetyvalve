
from django.conf.urls import patterns, url


urlpatterns = patterns('person.views',
    url(r'^login/$', 'login_view', name='login'),
    url(r'^logout/$', 'logout_view', name='logout'),
    url(r'^signatures/$', 'signatures', name='signatures'),

    (r'^test_auth/$', 'test_auth'),
)
