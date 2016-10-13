# coding=utf-8
from __future__ import unicode_literals

from django.template import Template, Context

from django.utils.encoding import python_2_unicode_compatible

from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django_pandas.io import read_frame
import pandas as pd

from fontawesome.fields import IconField
from unidecode import unidecode


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

    class Meta:
        verbose_name_plural = u"Indicadores"

    def dados(self, regionalizacao='munic'):
        df = read_frame(self.dado_set.filter(localidade__tipo=regionalizacao)).pivot(index='localidade', columns='ano', values='valor')
        df['_'] = df.index.map(unidecode)
        return df.sort_values(by='_').drop(labels=['_'], axis=1)

    def dados_html(self):
        return self.dados().to_html(classes=['table', 'table-striped'])


class Dado(NamedModel):
    indicador = models.ForeignKey(Indicador)
    localidade = models.ForeignKey(Localidade)
    ano = models.IntegerField()
    valor = models.CharField(max_length=100)

    class Meta:
        unique_together = (('indicador', 'localidade', 'ano'),)


@python_2_unicode_compatible
class Dashboard(models.Model):
    titulo = models.CharField(max_length=250)
    descricao = models.TextField(u"Descrição")
    ordem = models.PositiveIntegerField(default=0, blank=False, null=False)
    publicado = models.BooleanField(default=False)
    icone = IconField()

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ('ordem',)


class Modelo(NamedModel):
    html = models.TextField()
    css = models.TextField()
    js = models.TextField()
    last_update = models.DateTimeField(auto_now=True)

    def render(self, context):
        t = Template(self.html)
        context['object'] = self
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
