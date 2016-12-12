# coding=utf-8
import re
import pandas as pd
from collections import OrderedDict

import pygal
from bokeh.embed import components
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, FactorRange, Range1d, Plot, Rect, CategoricalAxis, LinearAxis, GlyphRenderer
from bokeh.charts import Line, HeatMap
from bokeh.resources import CDN
from django_pandas.io import read_frame

from data.models import Dado, IndicadorFluxo


def piramide_populacional(painel):
    indicadores = painel.indicadores.all()
    localidade = painel.localidades.first()
    ano = painel.periodos

    faixas = []
    for i in indicadores:
        inicio, _, final = re.search(r'(\d+) (a (\d+) anos|anos e mais)', i.nome).groups()
        if final is None:
            faixas.append((int(inicio), final))
        else:
            faixas.append((int(inicio), int(final)))
    faixas = sorted(set(faixas))

    source_dict = OrderedDict()
    cats = ['{}{}{}'.format(x, '-' if y else '+', y or '') for x, y in faixas]
    source_dict['cat'] = ['{}:0.5'.format(_) for _ in cats]


    qs_base = Dado.objects.filter(indicador__in=indicadores, localidade=localidade, ano=ano).order_by('indicador__nome')
    source_dict['Homens'] = pd.to_numeric(read_frame(qs_base.filter(indicador__nome__istartswith='homens')).valor)
    source_dict['midHomens'] = source_dict['Homens']/2

    source_dict['Mulheres'] = pd.to_numeric(read_frame(qs_base.filter(indicador__nome__istartswith='mulheres')).valor)
    source_dict['midMulheres'] = source_dict['Mulheres']/2

    source = ColumnDataSource(source_dict)

    bar_height = 0.8
    max_value = max(float(d.valor) for d in qs_base.all())
    ydr = FactorRange(factors=cats)
    xdr_left = Range1d(max_value, 0)
    xdr_right = Range1d(0, max_value)
    plot_height = 600
    plot_width = 1078

    plot_left = Plot(x_range=xdr_left, y_range=ydr, plot_height=plot_height,
                     plot_width=int(plot_width / 2))
    plot_left.title.text = 'Homens'
    plot_right = Plot(x_range=xdr_right, y_range=ydr, plot_height=plot_height,
                      plot_width=int(plot_width / 2))
    plot_right.title.text = 'Mulheres'

    plot_left.add_layout(CategoricalAxis(), 'left')
    plot_right.add_layout(LinearAxis(), 'below')
    plot_left.add_layout(LinearAxis(), 'below')

    # Set up the ranges, plot, and axes
    left_rect = Rect(y='cat',
                     x='midHomens',
                     width='Homens',
                     height=bar_height,
                     fill_color="#b3cde3",
                     line_color=None)
    right_rect = Rect(y='cat',
                      x='midMulheres',
                      width='Mulheres',
                      height=bar_height,
                      fill_color="#fbb4ae",
                      line_color=None)

    left_glyph = GlyphRenderer(data_source=source, glyph=left_rect)
    right_glyph = GlyphRenderer(data_source=source, glyph=right_rect)

    plot_left.renderers.extend([left_glyph])
    plot_right.renderers.extend([right_glyph])

    plot_left.min_border_right = 0
    plot_right.min_border_left = 0
    plot_left.outline_line_alpha = 0
    plot_right.outline_line_alpha = 0

    g = gridplot([[plot_left, plot_right]], border_space=0)

    script, div = components(g, CDN)
    return {'div': div, 'script': script}


def linechart_ano_valor(painel):
    indicadores = painel.indicadores.all()
    localidades = painel.localidades.all()
    if painel.periodos == u'0':
        qs = Dado.objects.filter(indicador__in=indicadores, localidade__in=localidades)
    else:
        anos = [int(ano) for ano in painel.periodos.split(',')]
        qs = Dado.objects.filter(indicador__in=indicadores, localidade__in=localidades, ano__in=anos)

    df = read_frame(qs)
    df.valor = pd.to_numeric(df.valor)
    g = Line(df, x='ano', y='valor', ylabel=u'população', plot_width=1078, plot_height=500)
    script, div = components(g, CDN)
    return {'div': div, 'script': script}


def heatmap_chart_indicador(indicador):
    df = read_frame(indicador.dadofluxo_set.all())
    df.valor = pd.to_numeric(df.valor)
    g = HeatMap(
        df,
        x='origem', y='destino', values='valor', stat=None,
        sort_dim={'x': False},
        width=1005, plot_height=1005,
        #x_axis_location="above",
        #width=600, plot_height=600
    )
    script, div = components(g, CDN)
    return {'div': div, 'script': script}


def pie_chart_simples(painel):
    df = painel.dataframe()
    c = pygal.Pie(
        legend_at_bottom=True,
        legend_at_bottom_columns=1,
    )
    for k, v in painel.dataframe().iterrows():
        c.add(v.indicador, float(v.valor))

    return c


def bar_chart_localidade(painel):
    df = painel.dataframe()
    c = pygal.Bar(
        legend_at_bottom=True,
        legend_at_bottom_columns=2,
    )
    for k, v in painel.dataframe().iterrows():
        c.add(v.localidade, float(v.valor))

    return c
