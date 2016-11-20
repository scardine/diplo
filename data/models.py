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
        ('drs', u'Departamentos Regionais de Saúde'),
        ('rras', u'Redes Regionais de Atenção à Saúde'),
        ('munic', u'Municípios Paulistas'),
    )
    codigo = models.CharField(max_length=30, blank=True, null=True)
    sublocalidades = models.ManyToManyField('self')
    tipo = models.CharField(max_length=60, choices=TIPO)


class Indicador(NamedModel):
    descricao = models.TextField(u"Descrição", null=True, blank=True)
    observacao = models.TextField(u"Observações", null=True, blank=True)
    periodo = models.CharField(max_length=250, null=True, blank=True)
    formato = models.CharField(max_length=50, default='', blank=True, help_text=u'Por exemplo: %0.3f formata com 3 casas depois da vírgula.')
    fonte = models.ForeignKey(Fonte)
    tema = models.ForeignKey(Tema)
    categoria = models.ForeignKey('Categoria', null=True)

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
        df = read_frame(self.dado_set.filter(localidade__tipo=regionalizacao)).pivot(index='localidade', columns='ano', values='valor')
        r = {
            "anos": [str(_) for _ in df.columns.values],
            "series": [],
            "meta": {
                '*': {
                    'scale': 'quantile',
                    'colors': colorbrewer['YlGnBu'][7]
                },
            }
        }
        for ano in r["anos"]:
            r["meta"][ano] = {
                "domain": sorted(v.strip() for v in df[int(ano)].unique() if v.strip())
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
    COMPLEXIDADE = (
        ('', u'N/D ou N/A'),
        ('media', u'M\xe9dia complexidade'),
        ('alta', u'Alta complexidade'),
    )
    ESPECIALIDADE = (
        ('cirurgia pediatrica', u'Cir\xfargico pedi\xe1trico (menor de 14 anos)'),
        ('cirurgia adulto', u'Cir\xfargico adulto (14 anos ou mais)'),
        ('leito dia', u'Leito Dia'),
    )
    complexidade = models.CharField(max_length=30, choices=COMPLEXIDADE)
    especialidade = models.CharField(max_length=100, null=True, blank=True, choices=ESPECIALIDADE, help_text=u'Especialidade do leito')
    subgrupo = models.CharField(max_length=100, help_text=u'Subgrupo de procedimento')
    menu = models.BooleanField(u"Exibir entrada no menu", default=True)

    class Meta:
        verbose_name_plural = u"Indicadores Fluxo"
        ordering = (u"subgrupo",)

    def dados(self, regionalizacao='munic'):
        df = read_frame(self.dadofluxo_set.filter(localidade__tipo=regionalizacao)).pivot(index='localidade', columns='ano', values='valor')
        df['_'] = df.index.map(unidecode)
        return df.sort_values(by='_').drop(labels=['_'], axis=1)

    def dataframe(self, regionalizacao='munic'):
        df = read_frame(self.dadofluxo_set.filter(localidade__tipo=regionalizacao))
        df.valor = df.valor.astype(float)
        return df

    def dados_html(self):
        return self.dados().to_html(classes=['table', 'table-striped'])

    def chart_data(self):
        return """{"nodes":[{"name":"Myriel","group":1},{"name":"Napoleon","group":1},{"name":"Mlle.Baptistine","group":1},{"name":"Mme.Magloire","group":1},{"name":"CountessdeLo","group":1},{"name":"Geborand","group":1},{"name":"Champtercier","group":1},{"name":"Cravatte","group":1},{"name":"Count","group":1},{"name":"OldMan","group":1},{"name":"Labarre","group":2},{"name":"Valjean","group":2},{"name":"Marguerite","group":3},{"name":"Mme.deR","group":2},{"name":"Isabeau","group":2},{"name":"Gervais","group":2},{"name":"Tholomyes","group":3},{"name":"Listolier","group":3},{"name":"Fameuil","group":3},{"name":"Blacheville","group":3},{"name":"Favourite","group":3},{"name":"Dahlia","group":3},{"name":"Zephine","group":3},{"name":"Fantine","group":3},{"name":"Mme.Thenardier","group":4},{"name":"Thenardier","group":4},{"name":"Cosette","group":5},{"name":"Javert","group":4},{"name":"Fauchelevent","group":0},{"name":"Bamatabois","group":2},{"name":"Perpetue","group":3},{"name":"Simplice","group":2},{"name":"Scaufflaire","group":2},{"name":"Woman1","group":2},{"name":"Judge","group":2},{"name":"Champmathieu","group":2},{"name":"Brevet","group":2},{"name":"Chenildieu","group":2},{"name":"Cochepaille","group":2},{"name":"Pontmercy","group":4},{"name":"Boulatruelle","group":6},{"name":"Eponine","group":4},{"name":"Anzelma","group":4},{"name":"Woman2","group":5},{"name":"MotherInnocent","group":0},{"name":"Gribier","group":0},{"name":"Jondrette","group":7},{"name":"Mme.Burgon","group":7},{"name":"Gavroche","group":8},{"name":"Gillenormand","group":5},{"name":"Magnon","group":5},{"name":"Mlle.Gillenormand","group":5},{"name":"Mme.Pontmercy","group":5},{"name":"Mlle.Vaubois","group":5},{"name":"Lt.Gillenormand","group":5},{"name":"Marius","group":8},{"name":"BaronessT","group":5},{"name":"Mabeuf","group":8},{"name":"Enjolras","group":8},{"name":"Combeferre","group":8},{"name":"Prouvaire","group":8},{"name":"Feuilly","group":8},{"name":"Courfeyrac","group":8},{"name":"Bahorel","group":8},{"name":"Bossuet","group":8},{"name":"Joly","group":8},{"name":"Grantaire","group":8},{"name":"MotherPlutarch","group":9},{"name":"Gueulemer","group":4},{"name":"Babet","group":4},{"name":"Claquesous","group":4},{"name":"Montparnasse","group":4},{"name":"Toussaint","group":5},{"name":"Child1","group":10},{"name":"Child2","group":10},{"name":"Brujon","group":4},{"name":"Mme.Hucheloup","group":8}],"links":[{"source":1,"target":0,"value":1},{"source":2,"target":0,"value":8},{"source":3,"target":0,"value":10},{"source":3,"target":2,"value":6},{"source":4,"target":0,"value":1},{"source":5,"target":0,"value":1},{"source":6,"target":0,"value":1},{"source":7,"target":0,"value":1},{"source":8,"target":0,"value":2},{"source":9,"target":0,"value":1},{"source":11,"target":10,"value":1},{"source":11,"target":3,"value":3},{"source":11,"target":2,"value":3},{"source":11,"target":0,"value":5},{"source":12,"target":11,"value":1},{"source":13,"target":11,"value":1},{"source":14,"target":11,"value":1},{"source":15,"target":11,"value":1},{"source":17,"target":16,"value":4},{"source":18,"target":16,"value":4},{"source":18,"target":17,"value":4},{"source":19,"target":16,"value":4},{"source":19,"target":17,"value":4},{"source":19,"target":18,"value":4},{"source":20,"target":16,"value":3},{"source":20,"target":17,"value":3},{"source":20,"target":18,"value":3},{"source":20,"target":19,"value":4},{"source":21,"target":16,"value":3},{"source":21,"target":17,"value":3},{"source":21,"target":18,"value":3},{"source":21,"target":19,"value":3},{"source":21,"target":20,"value":5},{"source":22,"target":16,"value":3},{"source":22,"target":17,"value":3},{"source":22,"target":18,"value":3},{"source":22,"target":19,"value":3},{"source":22,"target":20,"value":4},{"source":22,"target":21,"value":4},{"source":23,"target":16,"value":3},{"source":23,"target":17,"value":3},{"source":23,"target":18,"value":3},{"source":23,"target":19,"value":3},{"source":23,"target":20,"value":4},{"source":23,"target":21,"value":4},{"source":23,"target":22,"value":4},{"source":23,"target":12,"value":2},{"source":23,"target":11,"value":9},{"source":24,"target":23,"value":2},{"source":24,"target":11,"value":7},{"source":25,"target":24,"value":13},{"source":25,"target":23,"value":1},{"source":25,"target":11,"value":12},{"source":26,"target":24,"value":4},{"source":26,"target":11,"value":31},{"source":26,"target":16,"value":1},{"source":26,"target":25,"value":1},{"source":27,"target":11,"value":17},{"source":27,"target":23,"value":5},{"source":27,"target":25,"value":5},{"source":27,"target":24,"value":1},{"source":27,"target":26,"value":1},{"source":28,"target":11,"value":8},{"source":28,"target":27,"value":1},{"source":29,"target":23,"value":1},{"source":29,"target":27,"value":1},{"source":29,"target":11,"value":2},{"source":30,"target":23,"value":1},{"source":31,"target":30,"value":2},{"source":31,"target":11,"value":3},{"source":31,"target":23,"value":2},{"source":31,"target":27,"value":1},{"source":32,"target":11,"value":1},{"source":33,"target":11,"value":2},{"source":33,"target":27,"value":1},{"source":34,"target":11,"value":3},{"source":34,"target":29,"value":2},{"source":35,"target":11,"value":3},{"source":35,"target":34,"value":3},{"source":35,"target":29,"value":2},{"source":36,"target":34,"value":2},{"source":36,"target":35,"value":2},{"source":36,"target":11,"value":2},{"source":36,"target":29,"value":1},{"source":37,"target":34,"value":2},{"source":37,"target":35,"value":2},{"source":37,"target":36,"value":2},{"source":37,"target":11,"value":2},{"source":37,"target":29,"value":1},{"source":38,"target":34,"value":2},{"source":38,"target":35,"value":2},{"source":38,"target":36,"value":2},{"source":38,"target":37,"value":2},{"source":38,"target":11,"value":2},{"source":38,"target":29,"value":1},{"source":39,"target":25,"value":1},{"source":40,"target":25,"value":1},{"source":41,"target":24,"value":2},{"source":41,"target":25,"value":3},{"source":42,"target":41,"value":2},{"source":42,"target":25,"value":2},{"source":42,"target":24,"value":1},{"source":43,"target":11,"value":3},{"source":43,"target":26,"value":1},{"source":43,"target":27,"value":1},{"source":44,"target":28,"value":3},{"source":44,"target":11,"value":1},{"source":45,"target":28,"value":2},{"source":47,"target":46,"value":1},{"source":48,"target":47,"value":2},{"source":48,"target":25,"value":1},{"source":48,"target":27,"value":1},{"source":48,"target":11,"value":1},{"source":49,"target":26,"value":3},{"source":49,"target":11,"value":2},{"source":50,"target":49,"value":1},{"source":50,"target":24,"value":1},{"source":51,"target":49,"value":9},{"source":51,"target":26,"value":2},{"source":51,"target":11,"value":2},{"source":52,"target":51,"value":1},{"source":52,"target":39,"value":1},{"source":53,"target":51,"value":1},{"source":54,"target":51,"value":2},{"source":54,"target":49,"value":1},{"source":54,"target":26,"value":1},{"source":55,"target":51,"value":6},{"source":55,"target":49,"value":12},{"source":55,"target":39,"value":1},{"source":55,"target":54,"value":1},{"source":55,"target":26,"value":21},{"source":55,"target":11,"value":19},{"source":55,"target":16,"value":1},{"source":55,"target":25,"value":2},{"source":55,"target":41,"value":5},{"source":55,"target":48,"value":4},{"source":56,"target":49,"value":1},{"source":56,"target":55,"value":1},{"source":57,"target":55,"value":1},{"source":57,"target":41,"value":1},{"source":57,"target":48,"value":1},{"source":58,"target":55,"value":7},{"source":58,"target":48,"value":7},{"source":58,"target":27,"value":6},{"source":58,"target":57,"value":1},{"source":58,"target":11,"value":4},{"source":59,"target":58,"value":15},{"source":59,"target":55,"value":5},{"source":59,"target":48,"value":6},{"source":59,"target":57,"value":2},{"source":60,"target":48,"value":1},{"source":60,"target":58,"value":4},{"source":60,"target":59,"value":2},{"source":61,"target":48,"value":2},{"source":61,"target":58,"value":6},{"source":61,"target":60,"value":2},{"source":61,"target":59,"value":5},{"source":61,"target":57,"value":1},{"source":61,"target":55,"value":1},{"source":62,"target":55,"value":9},{"source":62,"target":58,"value":17},{"source":62,"target":59,"value":13},{"source":62,"target":48,"value":7},{"source":62,"target":57,"value":2},{"source":62,"target":41,"value":1},{"source":62,"target":61,"value":6},{"source":62,"target":60,"value":3},{"source":63,"target":59,"value":5},{"source":63,"target":48,"value":5},{"source":63,"target":62,"value":6},{"source":63,"target":57,"value":2},{"source":63,"target":58,"value":4},{"source":63,"target":61,"value":3},{"source":63,"target":60,"value":2},{"source":63,"target":55,"value":1},{"source":64,"target":55,"value":5},{"source":64,"target":62,"value":12},{"source":64,"target":48,"value":5},{"source":64,"target":63,"value":4},{"source":64,"target":58,"value":10},{"source":64,"target":61,"value":6},{"source":64,"target":60,"value":2},{"source":64,"target":59,"value":9},{"source":64,"target":57,"value":1},{"source":64,"target":11,"value":1},{"source":65,"target":63,"value":5},{"source":65,"target":64,"value":7},{"source":65,"target":48,"value":3},{"source":65,"target":62,"value":5},{"source":65,"target":58,"value":5},{"source":65,"target":61,"value":5},{"source":65,"target":60,"value":2},{"source":65,"target":59,"value":5},{"source":65,"target":57,"value":1},{"source":65,"target":55,"value":2},{"source":66,"target":64,"value":3},{"source":66,"target":58,"value":3},{"source":66,"target":59,"value":1},{"source":66,"target":62,"value":2},{"source":66,"target":65,"value":2},{"source":66,"target":48,"value":1},{"source":66,"target":63,"value":1},{"source":66,"target":61,"value":1},{"source":66,"target":60,"value":1},{"source":67,"target":57,"value":3},{"source":68,"target":25,"value":5},{"source":68,"target":11,"value":1},{"source":68,"target":24,"value":1},{"source":68,"target":27,"value":1},{"source":68,"target":48,"value":1},{"source":68,"target":41,"value":1},{"source":69,"target":25,"value":6},{"source":69,"target":68,"value":6},{"source":69,"target":11,"value":1},{"source":69,"target":24,"value":1},{"source":69,"target":27,"value":2},{"source":69,"target":48,"value":1},{"source":69,"target":41,"value":1},{"source":70,"target":25,"value":4},{"source":70,"target":69,"value":4},{"source":70,"target":68,"value":4},{"source":70,"target":11,"value":1},{"source":70,"target":24,"value":1},{"source":70,"target":27,"value":1},{"source":70,"target":41,"value":1},{"source":70,"target":58,"value":1},{"source":71,"target":27,"value":1},{"source":71,"target":69,"value":2},{"source":71,"target":68,"value":2},{"source":71,"target":70,"value":2},{"source":71,"target":11,"value":1},{"source":71,"target":48,"value":1},{"source":71,"target":41,"value":1},{"source":71,"target":25,"value":1},{"source":72,"target":26,"value":2},{"source":72,"target":27,"value":1},{"source":72,"target":11,"value":1},{"source":73,"target":48,"value":2},{"source":74,"target":48,"value":2},{"source":74,"target":73,"value":3},{"source":75,"target":69,"value":3},{"source":75,"target":68,"value":3},{"source":75,"target":25,"value":3},{"source":75,"target":48,"value":1},{"source":75,"target":41,"value":1},{"source":75,"target":70,"value":1},{"source":75,"target":71,"value":1},{"source":76,"target":64,"value":1},{"source":76,"target":65,"value":1},{"source":76,"target":66,"value":1},{"source":76,"target":63,"value":1},{"source":76,"target":62,"value":1},{"source":76,"target":48,"value":1},{"source":76,"target":58,"value":1}]}"""

    def __str__(self):
        return self.subgrupo


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
        return self.indicador_set.first()

    def __str__(self):
        parent = self.get_parent()
        if parent:
            return u"{} > {}".format(parent, self.nome)
        return self.nome



