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
from django.conf.urls import url, include
from django.contrib import admin
from data import views as data_views
from home import views as home_views
from django_markdown import flatpages
admin.autodiscover()
flatpages.register()

urlpatterns = [
    url(r'^$', home_views.Index.as_view(), name='home'),
    url(r'^glossario/', include('glossario.urls')),
    #url(r'^$', data_views.Home.as_view(), name='home', kwargs={'dashboard': '', 'localidades': 'munic'}),
    url(r'^dashboard/(?P<dashboard>\d+)/(?P<localidades>\w+)/$', data_views.Home.as_view(), name='dashboard'),
    # url(r'^tema/$', data_views.TemaList.as_view(), name='tema-list'),
    url(r'^tema/mapa/$', data_views.IndicadorMapList.as_view(), name='indicador-map-list', kwargs={'tema': ''}),
    url(r'^tema/$', data_views.IndicadorList.as_view(), name='indicador-list', kwargs={'tema': ''}),
    url(r'^tema/mapa/(?P<tema>\d+)/$', data_views.IndicadorMapList.as_view(), name='indicador-map-list'),
    url(r'^indicadores/(?P<slug>[-\w\d]+)/$', data_views.CategoriaDetail.as_view(), name='categoria-detail'),
    url(r'^tema/(?P<tema>\d+)/$', data_views.IndicadorList.as_view(), name='indicador-list'),
    url(r'^tema/mapa/(?P<tema>\d+)/(?P<pk>\d+)/$', data_views.IndicadorMap.as_view(), name='indicador-map-detail'),
    url(r'^tema/mapa/(?P<tema>\d+)/(?P<pk>\d+)/(?P<regionalizacao>\w+)/$', data_views.IndicadorMap.as_view(), name='indicador-map-detail'),
    url(r'^tema/(?P<tema>\d+)/(?P<pk>\d+)/$', data_views.IndicadorDetail.as_view(), name='indicador-detail'),
    url(r'^tema/(?P<tema>\d+)/(?P<pk>\d+)/(?P<regionalizacao>\w+)/$', data_views.IndicadorDetail.as_view(), name='indicador-detail'),
    url(r'^conteudo/', include('django.contrib.flatpages.urls')),
    url(r'^markdown/', include( 'django_markdown.urls')),
    url(r'^admin/', admin.site.urls),
]

admin.site.site_header = 'Painel de Controle'
