from django.conf import settings
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'petition.views.popular', name='popular'),
    url(r'^ollmal/$', 'petition.views.all', name='all'),
    url(r'^um-okkur/$', 'core.views.about_us', name='about_us'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        # Testing
        url(r'^test-mail/$', 'core.views.test_mail', name='test_mail'),
    )

