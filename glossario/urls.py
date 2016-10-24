from django.conf.urls import url

from views import TermoList

urlpatterns = [
    url(r'^$', TermoList.as_view(), name='glossario'),
]
