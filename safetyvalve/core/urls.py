from django.conf import settings
from django.conf.urls import patterns, url
from petition import views as petition_views
from core import views as core_views

urlpatterns = [
    url(r'^$', petition_views.popular, name='popular'),
    url(r'^ollmal/$', petition_views.all, name='all'),
    url(r'^um-okkur/$', core_views.about_us, name='about_us'),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^test-mail/$', core_views.test_mail, name='test_mail'),
    ]
