from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from data.models import Tema, Indicador


class Home(TemplateView):
    template_name = 'home.html'


class TemaList(ListView):
    template_name = 'tema-list.html'
    queryset = Tema.objects.all()


class IndicadorList(ListView):
    template_name = 'indicador-list.html'

    def get_queryset(self):
        tema = get_object_or_404(Tema, pk=self.kwargs.get('tema'))
        return tema.indicador_set.all()


class IndicadorDetail(DetailView):
    template_name = 'indicador-detail.html'
    queryset = Indicador.objects.all()
