# coding=utf-8
from __future__ import unicode_literals

import json

from django.template import Template, Context

from django.utils.encoding import python_2_unicode_compatible

from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.utils.text import slugify
from django_pandas.io import read_frame
import pandas as pd

from fontawesome.fields import IconField
from treebeard.mp_tree import MP_Node
from unidecode import unidecode

from data.colorbrewer import colorbrewer


@python_2_unicode_compatible
class NamedModel(models.Model):
    nome = models.CharField(max_length=150)

    def __str__(self):
        return self.nome

    class Meta:
        abstract = True


class Fonte(NamedModel):
    descricao = models.TextField(null=True, blank=True)
    url = models.URLField(blank=True, null=True)


class Tema(NamedModel):
    descricao = models.TextField(null=True, blank=True)
    ordem = models.PositiveIntegerField(default=0, blank=False, null=False)
    dashboard = models.BooleanField(u'Exibir no menu de dashboards?', default=False)

    class Meta:
        ordering = ('ordem', 'nome')


class Localidade(NamedModel):
    TIPO = (
        ('uf', u'Estado de São Paulo'),
        ('regsau', u'Regiões de Saúde'),
        ('pesquisa', u'Regiões de Saúde da Pesquisa'),
        ('mun_pesquisa', u'Municípios da Pesquisa'),
        ('drs', u'Departamentos Regionais de Saúde'),
        ('rras', u'Redes Regionais de Atenção à Saúde'),
        ('munic', u'Municípios Paulistas'),
    )
    codigo = models.CharField(max_length=30, blank=True, null=True)
    sublocalidades = models.ManyToManyField('self')
    tipo = models.CharField(max_length=60, choices=TIPO)


class Indicador(NamedModel):
    TIPO = (
        ('quantitativo', u"Quantitativo - quantil"),
        ('categorico', u"Categórico"),
        ('ordinal', u"Quantitativo - ordinal"),
    )
    descricao = models.TextField(u"Descrição", null=True, blank=True)
    observacao = models.TextField(u"Observações", null=True, blank=True)
    periodo = models.CharField(max_length=250, null=True, blank=True)
    formato = models.CharField(max_length=50, default='', blank=True, help_text=u'Por exemplo: %0.3f formata com 3 casas depois da vírgula.')
    fontes = models.ManyToManyField(Fonte)
    tema = models.ForeignKey(Tema)
    categoria = models.ForeignKey('Categoria', null=True)
    tipo = models.CharField(max_length=30, choices=TIPO, default="quantitativo")

    class Meta:
        verbose_name_plural = u"Indicadores"
        ordering = (u"nome",)

    def dados(self, regionalizacao='munic'):
        df = read_frame(self.dado_set.filter(localidade__tipo=regionalizacao)).pivot(index='localidade', columns='ano', values='valor')
        df['_'] = df.index.map(unidecode)
        return df.sort_values(by='_').drop(labels=['_'], axis=1)

    def anos(self):
        return self.periodo.split(',')

    def map_data(self, regionalizacao='munic'):
        d1 = read_frame(self.dado_set.filter(localidade__tipo=regionalizacao))
        df = d1.pivot(index='localidade', columns='ano', values='valor')
        r = {
            "anos": [str(_) for _ in df.columns.values],
            "series": [],
        }
        if self.tipo == "categorico":
            dominio = list(d1.valor.unique())
            r["meta"] = {
                '*': {
                    'scale': 'ordinal',
                    'domain': dominio,
                    'valueLabels': dominio,
                    'colors': colorbrewer['Set1'][9][:len(dominio)]
                },
            }
        elif self.tipo == "quantitativo":
            r["meta"] = {
                '*': {
                    'scale': 'quantile',
                    'colors': colorbrewer['YlGnBu'][7]
                },
            }
            for ano in r["anos"]:
                r["meta"][ano] = {
                    "domain": sorted(v.strip() for v in df[int(ano)].unique() if v.strip())
                }
        else:
            r["meta"] = {
                '*': {
                    'scale': 'threshold',
                    'colors': colorbrewer['YlGnBu'][5],
                    'numberFormat': ',.02f',
                },
            }
            for ano in r["anos"]:
                r["meta"][ano] = {
                    "domain": [20, 40, 60, 80, 100]
                }

        for line in df.iterrows():
            d = dict(line[1])
            d['localidade'] = line[0]
            r["series"].append(d)
        return json.dumps(r)

    def dataframe(self, regionalizacao='munic'):
        df = read_frame(self.dado_set.filter(localidade__tipo=regionalizacao))
        df.valor = df.valor.astype(float)
        return df

    def dados_html(self):
        return self.dados().to_html(classes=['table', 'table-striped'])


class Dado( models.Model):
    indicador = models.ForeignKey(Indicador)
    localidade = models.ForeignKey(Localidade)
    ano = models.IntegerField()
    valor = models.CharField(max_length=100)

    class Meta:
        unique_together = (('indicador', 'localidade', 'ano'),)


@python_2_unicode_compatible
class IndicadorFluxo(models.Model):
    categoria = models.ForeignKey('Categoria', null=True, blank=True)
    nome = models.CharField(max_length=100)
    menu = models.BooleanField(u"Exibir entrada no menu", default=True)
    subgrupo = True

    class Meta:
        verbose_name_plural = u"Indicadores Fluxo"
        ordering = (u"nome",)

    def dados(self, regionalizacao='munic'):
        df = read_frame(self.dadofluxo_set.exclude(valor=None)).pivot(index='origem', columns='destino', values='valor')
        df['_'] = df.index.map(unidecode)
        return df.sort_values(by='_').drop(labels=['_'], axis=1)

    def dataframe(self, regionalizacao='munic'):
        df = read_frame(self.dadofluxo_set.exclude(valor=None))
        df.valor = df.valor.astype(float)
        return df

    def dados_html(self):
        return self.dados().replace([None], ['-']).to_html(classes=['table', 'table-striped'], na_rep='-')

    def __str__(self):
        return self.nome


class DadoFluxo(models.Model):
    indicador = models.ForeignKey(IndicadorFluxo)
    origem = models.ForeignKey(Localidade, related_name='dados_origem')
    destino = models.ForeignKey(Localidade, related_name='dados_destino')
    ano = models.IntegerField()
    valor = models.CharField(max_length=100)

    class Meta:
        unique_together = (('indicador', 'origem', 'destino', 'ano'),)


@python_2_unicode_compatible
class Dashboard(models.Model):
    titulo = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)
    categoria = models.ForeignKey('Categoria')
    descricao = models.TextField(u"Descrição")
    ordem = models.PositiveIntegerField(default=0, blank=False, null=False)
    publicado = models.BooleanField(default=False)
    icone = IconField()

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ('ordem',)


class Modelo(NamedModel):
    html = models.TextField(default='<!-- -->')
    css = models.TextField(default='<style></style>')
    js = models.TextField(default='<script></script>')
    last_update = models.DateTimeField(auto_now=True)

    def get_template(self):
        return Template(self.html)

    def render(self, context):
        t = self.get_template()
        return t.render(context)


@python_2_unicode_compatible
class Painel(models.Model):
    dashboard = models.ForeignKey(Dashboard)
    icone = IconField()
    titulo = models.CharField(max_length=250)
    ordem = models.PositiveIntegerField(default=0, blank=False, null=False)
    css_class = models.TextField(default='col-lg-12')
    indicadores = models.ManyToManyField(Indicador)
    localidades = models.ManyToManyField(Localidade)
    periodos = models.CharField(max_length=250, blank=True, null=True, validators=[validate_comma_separated_integer_list])
    modelo = models.ForeignKey(Modelo)

    def __str__(self):
        return self.titulo

    def qs(self):
        qs = Dado.objects.filter(
            indicador__in=self.indicadores.all(),
            localidade__in=self.localidades.all(),
        )
        if self.periodos == u'0':
            return qs
        return qs.filter(periodo__in=[int(_) for _ in self.periodos.split(',')])

    def dataframe(self):
        return read_frame(self.qs())

    class Meta:
        ordering = ('ordem',)


@python_2_unicode_compatible
class Categoria(MP_Node):
    nome = models.CharField(max_length=300)
    subtitulo = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True, max_length=255)
    ordem = models.PositiveIntegerField(default=1)
    home = models.BooleanField(u'Exibir card na homepage', default=True)
    menu = models.BooleanField(u'Exibir entrada no menu', default=True)

    node_order_by = ('ordem', 'nome')

    def indicador(self):
        indicador = Indicador.objects.filter(categoria__in=self.get_descendants()).first()
        if indicador:
            return indicador
        indicador = IndicadorFluxo.objects.filter(categoria__in=self.get_descendants()).first()
        if indicador:
            return indicador
        return self.indicador_set.first()

    def variaveis(self):
        for v in self.indicador_set.all():
            yield v
        for v in self.indicadorfluxo_set.all():
            yield v

    def __str__(self):
        parent = self.get_parent()
        if parent:
            return u"{} > {}".format(parent, self.nome)
        return self.nome


@python_2_unicode_compatible
class DadoPrimario(models.Model):
    nome = models.CharField(max_length=300)
    descricao = models.TextField(null=True, blank=True)
    ordem = models.PositiveIntegerField(default=1)
    arquivo = models.FileField(upload_to='dados-primarios')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = u'Dados Primários'
        verbose_name = u'Dado Primário'
        ordering = ('ordem',)
