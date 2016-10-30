from django.conf.urls import url

from views import TermoList

urlpatterns = [
    url(r'^$', TermoList.as_view(), name='glossario'),
    url(r'^(?P<slug_termo>.+)/$', TermoList.as_view(), name='glossario'),
]
