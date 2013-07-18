
from django.conf.urls import patterns


urlpatterns = patterns('person.views',
    (r'^logout/$', 'logout_view'),
    (r'^signatures/$', 'signatures'),

    (r'^test_auth/$', 'test_auth'),
)
