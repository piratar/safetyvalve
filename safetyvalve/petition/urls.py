from django.conf.urls import patterns, url

from petition import views


urlpatterns = patterns('',
#    url(r'^popular/$', views.popular, name='popular'),
    
    url(r'^(?P<petition_id>\d+)/$', views.detail, name='detail'),

    url(r'^(?P<petition_id>\d+)/sign/$', views.sign, name='sign'),
    url(r'^(?P<petition_id>\d+)/unsign/$', views.unsign, name='unsign'),
    url(r'^(?P<petition_id>\d+)/sign_receipt/$', views.sign_receipt, name='sign_receipt'),
    url(r'^(?P<petition_id>\d+)/unsign_receipt/$', views.unsign_receipt, name='unsign_receipt'),
    url(r'^(?P<petition_id>\d+)/email/$', views.email, name='email'),
    url(r'^authenticate/$', views.authenticate, name='authenticate'),
)
