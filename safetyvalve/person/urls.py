
from django.conf.urls import patterns, url

from person import views


urlpatterns = patterns(
    'person.views',
    url(r'^innskra/$', 'login_view', name='login'),
    url(r'^utskra/$', 'logout_view', name='logout'),
    url(r'^minsida/$', 'my_page', name='my_page'),
    url(r'^minarundirskriftir/$', views.get_user_signatures, name='get_user_signatures')
)
