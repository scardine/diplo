from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView

from data.forms import TemaLocalForm, DashboardLocalForm
from data.models import Tema, Indicador, Dashboard, Localidade


class Home(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        d = super(Home, self).get_context_data(**kwargs)
        if kwargs['tema']:
            d['tema'] = get_object_or_404(Tema, pk=kwargs['tema'])
        else:
            d['tema'] = Tema.objects.filter(dashboard=True).first()
        d['localidades'] = Localidade.objects.filter(tipo=kwargs['localidades'])
        d['form'] = DashboardLocalForm(initial={'tema': d['tema'].pk})
        d['dashboard'] = Dashboard.objects.first()
        return d


class TemaList(ListView):
    template_name = 'tema-list.html'
    queryset = Tema.objects.all()


class IndicadorList(ListView):
    template_name = 'indicador-list.html'

    def get_tema(self):
        try:
            return self._tema
        except AttributeError:
            pass
        if self.kwargs['tema']:
            self._tema = get_object_or_404(Tema, pk=self.kwargs.get('tema'))
        else:
            self._tema = Tema.objects.filter(dashboard=True).first()
        return self._tema

    def get_queryset(self):
        return self.get_tema().indicador_set.all()

    def get_context_data(self, **kwargs):
        d = super(IndicadorList, self).get_context_data(**kwargs)
        d['tema'] = self.get_tema()
        d['form'] = TemaLocalForm(initial={'tema': d.get('tema')})
        return d


class IndicadorDetail(DetailView):
    template_name = 'indicador-detail.html'
    queryset = Indicador.objects.all()

    def get_context_data(self, **kwargs):
        d = super(IndicadorDetail, self).get_context_data(**kwargs)
        d['regionalizacao'] = self.kwargs.get('regionalizacao', 'munic')
        d['form'] = TemaLocalForm(initial={'localidades': d['regionalizacao']})
        d['ordem'] = self.request.GET.get('o', 'localidade')
        return d

