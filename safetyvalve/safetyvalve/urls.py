from django.conf.urls import patterns, include, url

from safetyvalve import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'petition.views.index', name='index'),
    # url(r'^safetyvalve/', include('safetyvalve.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^petition/', include('petition.urls')),
    url(r'^person/', include('person.urls')),
    url(r'^althingi/', include('althingi.urls')),

    url(r'^about-us/', views.about_us, name='about_us'),
)
