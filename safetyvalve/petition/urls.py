from django.conf.urls import patterns, url

from petition import views

urlpatterns = patterns('',
    url(r'^$',views.index, name='index'),
    url(r'^(?P<petition_id>\d+)/$', views.detail, name='detail')
)