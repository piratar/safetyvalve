from django.conf.urls import patterns, url

from petition import views


urlpatterns = patterns('',
#    url(r'^vinsaelt/$', views.popular, name='popular'),
    
    url(r'^(?P<petition_id>\d+)/$', views.detail, name='detail'),
    url(r'^(?P<petition_id>\d+)/undirskriftir/$', views.get_public_signatures, name='get_public_signatures'),

    url(r'^(?P<petition_id>\d+)/skra/(?P<stance>.+)/$', views.sign, name='sign'),
    url(r'^(?P<petition_id>\d+)/afskra/$', views.unsign, name='unsign'),
    url(r'^(?P<petition_id>\d+)/skraning_mottaka/$', views.sign_receipt, name='sign_receipt'),
    url(r'^(?P<petition_id>\d+)/afskraning_mottaka/$', views.unsign_receipt, name='unsign_receipt'),
    url(r'^(?P<petition_id>\d+)/email/$', views.email, name='email'),
    url(r'^search/$', views.search_terms, name='search_terms'),
    url(r'^search_results/(?P<search_terms>.+)$', views.search_results, name='search_results'),
    url(r'^audkenna/$', views.authenticate, name='authenticate'),
)
