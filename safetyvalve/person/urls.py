
from django.conf.urls import patterns


urlpatterns = patterns('person.views',
    (r'^test_auth/$', 'test_auth'),
)
