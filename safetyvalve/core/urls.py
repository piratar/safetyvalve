from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'petition.views.popular', name='popular'),
    url(r'^ollmal/$', 'petition.views.all', name='all'),
    url(r'^um-okkur/$', 'core.views.about_us', name='about_us'),
)
