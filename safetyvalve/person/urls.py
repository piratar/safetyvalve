
from django.conf.urls import patterns, url

from person import views


urlpatterns = [
    url(r'^innskra/$', views.login_view, name='login'),
    url(r'^utskra/$', views.logout_view, name='logout'),
    url(r'^minsida/$', views.my_page, name='my_page'),
    url(r'^minarundirskriftir/$', views.get_user_signatures, name='get_user_signatures')
]