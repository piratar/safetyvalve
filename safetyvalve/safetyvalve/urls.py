from django.conf.urls import patterns, include, url

#from safetyvalve import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

urlpatterns = [
    url(r'^', include('person.urls')),
    url(r'^', include('core.urls')),
    url(r'^frumvarp/', include('petition.urls')),
    

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
]
