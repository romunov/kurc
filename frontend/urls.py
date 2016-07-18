from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='welcome'),
    url(r'^settings$', views.settings, name='settings'),
    url(r'^docs$', views.docs, name='docs'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^login$', views.login, name='login')
]