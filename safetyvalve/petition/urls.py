from django.conf.urls import patterns, url

from petition import views

urlpatterns = patterns('',
    url(r'^$',views.index, name='index'),
    url(r'^(?P<petition_id>\d+)/$', views.detail, name='detail'),

    url(r'^(?P<petition_id>\d+)/sign/$', views.sign, name='sign'),
    url(r'^authenticate/$', views.authenticate, name='authenticate'),
)