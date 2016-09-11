from django.conf.urls import url
from . import views
from django.conf.urls import include, url

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^settings$', views.settings, name='settings'),
    url(r'^docs$', views.docs, name='docs'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^login$', views.login, name='login'),
    url(r'^welcome$', views.login, name="welcome"),
    url(r'^stats$', views.stats, name="stats"),
    url(r'^upload$', views.upload_file, name="upload_file"),
    url(r'^(?P<doc_id>[0-9]{1,4}$)', views.view_file, name='view_file'),
    url(r'^oauth2callback', views.auth_return, name='return'),
]
