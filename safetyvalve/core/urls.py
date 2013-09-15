from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'petition.views.index', name='index'),
    url(r'^um-okkur/$', 'core.views.about_us', name='about_us'),
)
