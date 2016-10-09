"""diplo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from data import views as data_views


urlpatterns = [
    url(r'^$', data_views.Home.as_view(), name='home', kwargs={'tema': '', 'localidades': 'munic'}),
    url(r'^dashboard/(?P<tema>\d+)/(?P<localidades>\w+)/$', data_views.Home.as_view(), name='home'),
    # url(r'^tema/$', data_views.TemaList.as_view(), name='tema-list'),
    url(r'^tema/$', data_views.IndicadorList.as_view(), name='indicador-list', kwargs={'tema': ''}),
    url(r'^tema/(?P<tema>\d+)/$', data_views.IndicadorList.as_view(), name='indicador-list'),
    url(r'^tema/(?P<tema>\d+)/(?P<pk>\d+)/$', data_views.IndicadorDetail.as_view(), name='indicador-detail'),
    url(r'^tema/(?P<tema>\d+)/(?P<pk>\d+)/(?P<regionalizacao>\w+)/$', data_views.IndicadorDetail.as_view(), name='indicador-detail'),
    url(r'^admin/', admin.site.urls),
]
