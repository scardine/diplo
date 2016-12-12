from django.http import HttpResponse
from django.shortcuts import get_object_or_404

# Create your views here.
from django.utils.text import slugify
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView

from data.forms import TemaLocalForm, DashboardLocalForm
from data.models import Tema, Indicador, Dashboard, Localidade, Categoria, IndicadorFluxo, DadoPrimario
from bokeh.charts import Bar
from bokeh.embed import components
from bokeh.resources import CDN

class Home(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        d = super(Home, self).get_context_data(**kwargs)
        d['localidades'] = Localidade.objects.filter(tipo=kwargs['localidades'])
        if kwargs.get('dashboard'):
            d['dashboard'] = get_object_or_404(Dashboard, pk=kwargs['dashboard'])
        else:
            d['dashboard'] = Dashboard.objects.filter(publicado=True).first()
        d['form'] = DashboardLocalForm(initial={'dashboard': d['dashboard'].pk, 'localidades': kwargs.get('localidades', 'munic')})
        return d


class TemaList(ListView):
    template_name = 'tema-list.html'
    queryset = Tema.objects.all()


class DashboardList(ListView):
    template_name = 'dashboard-list.html'
    queryset = Dashboard.objects.all()


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


class IndicadorMapList(IndicadorList):
    template_name = 'indicador-map-list.html'


class IndicadorDetail(DetailView):
    template_name = 'indicador-detail.html'
    queryset = Indicador.objects.all()

    def get_context_data(self, **kwargs):
        d = super(IndicadorDetail, self).get_context_data(**kwargs)
        d['regionalizacao'] = self.kwargs.get('regionalizacao', 'regsau')
        d['form'] = TemaLocalForm(initial={'localidades': d['regionalizacao']})
        d['ordem'] = self.request.GET.get('o', 'localidade')
        return d


class IndicadorMap(DetailView):
    template_name = 'indicador-detail-map.html'
    queryset = Indicador.objects.all()

    def get_context_data(self, **kwargs):
        d = super(IndicadorMap, self).get_context_data(**kwargs)
        d['regionalizacao'] = self.kwargs.get('regionalizacao', 'regsau')
        d['form'] = TemaLocalForm(initial={'localidades': d['regionalizacao']})
        d['ordem'] = self.request.GET.get('o', 'localidade')
        return d


def download_csv(request, pk, regionalizacao):
    indicador = get_object_or_404(Indicador, pk=pk)
    df = indicador.dataframe(regionalizacao).pivot(index='localidade', columns='ano', values='valor')
    r = HttpResponse(content_type='text/csv')
    r['Content-Disposition'] = 'attachment; filename="{}--{}--{}.csv"'.format(
        indicador.categoria.slug if indicador.categoria else slugify(indicador.tema.nome),
        slugify(indicador.nome),
        regionalizacao,
    )
    df.to_csv(r, sep=';', decimal=',', encoding='iso-8859-1')
    return r


def download_fluxo_csv(request, pk):
    indicador = get_object_or_404(IndicadorFluxo, pk=pk)
    df = indicador.dados().replace([None], ['-'])
    r = HttpResponse(content_type='text/csv')
    r['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(
        slugify(indicador.nome),
    )
    df.to_csv(r, sep=';', decimal=',', encoding='iso-8859-1')
    return r


class IndicadorChart(DetailView):
    template_name = 'indicador-detail-chart.html'
    queryset = Indicador.objects.all()

    def get_context_data(self, **kwargs):
        d = super(IndicadorChart, self).get_context_data(**kwargs)
        d['regionalizacao'] = self.kwargs.get('regionalizacao', 'regsau')
        d['form'] = TemaLocalForm(initial={'localidades': d['regionalizacao']})
        d['ordem'] = self.request.GET.get('o', 'localidade')
        return d


class IndicadorFluxoChart(DetailView):
    template_name = 'indicador-detail-fluxo.html'
    queryset = IndicadorFluxo.objects.all()

    def get_context_data(self, **kwargs):
        d = super(IndicadorFluxoChart, self).get_context_data(**kwargs)
        d['fluxo'] = d['object']
        return d

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.kwargs.get('pk', '*')
        if pk == '*':
            return queryset.first()
        return queryset.get(pk=pk)


class CategoriaDetail(DetailView):
    template_name = 'categoria-detail.html'
    queryset = Categoria.objects.all()


class CategoriaList(ListView):
    template_name = 'categoria-list.html'
    queryset = Categoria.objects.all()


class DashboardDetail(DetailView):
    template_name = 'dashboard-detail.html'
    queryset = Dashboard.objects.all()

    def get_context_data(self, **kwargs):
        d = super(DashboardDetail, self).get_context_data(**kwargs)
        d['menu_locais'] = {
            'sp': Localidade.objects.get(tipo='uf'),
            'regs': {reg:reg.sublocalidades.all() for reg in Localidade.objects.filter(tipo='pesquisa')}
        }
        localidade_id = self.kwargs.get('localidade_id')
        if localidade_id is None:
            localidade = d['menu_locais']['sp']
        else:
            localidade = Localidade.objects.get(pk=localidade_id)
        d['localidade'] = localidade
        d['paineis'] = d['object'].painel_set.filter(localidades=localidade)
        return d


class DadoPrimarioList(ListView):
    template_name = 'dado-primario-list.html'
    queryset = DadoPrimario.objects.all()
