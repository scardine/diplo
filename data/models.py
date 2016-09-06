# coding=utf-8
from __future__ import unicode_literals

from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django_pandas.io import read_frame
from fontawesome.fields import IconField


class NamedModel(models.Model):
    nome = models.CharField(max_length=150)

    def __unicode__(self):
        return self.nome

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

    class Meta:
        ordering = ('ordem', 'nome')


class Localidade(NamedModel):
    TIPO = (
        ('estado', u'Estado'),
        ('regiao', u'Região'),
        ('municipio', u'Município'),
    )
    codigo = models.CharField(max_length=30, blank=True, null=True)
    sublocalidades = models.ManyToManyField('self')
    tipo = models.CharField(max_length=60, choices=TIPO)


class Indicador(NamedModel):
    descricao = models.TextField(u"Descrição", null=True, blank=True)
    observacao = models.TextField(u"Observações", null=True, blank=True)
    periodo = models.CharField(max_length=250, null=True, blank=True)
    formato = models.CharField(max_length=50, default='', blank=True)
    fonte = models.ForeignKey(Fonte)
    tema = models.ForeignKey(Tema)
    class Meta:
        verbose_name_plural = u"Indicadores"

    def dados(self):
        return read_frame(self.dado_set.all()).pivot(index='localidade', columns='ano', values='valor')

    def dados_html(self):
        return self.dados().to_html(classes=['table', 'table-striped'])


class Dado(NamedModel):
    indicador = models.ForeignKey(Indicador)
    localidade = models.ForeignKey(Localidade)
    ano = models.IntegerField()
    valor = models.CharField(max_length=100)

    class Meta:
        unique_together = (('indicador', 'localidade', 'ano'),)


class Dashboard(models.Model):
    titulo = models.CharField(max_length=250)
    descricao = models.TextField(u"Descrição")
    ordem = models.PositiveIntegerField(default=0, blank=False, null=False)
    icone = IconField()

    def __unicode__(self):
        return self.titulo


class Modelo(NamedModel):
    html = models.TextField()
    css = models.TextField()
    js = models.TextField()
    last_update = models.DateTimeField(auto_now=True)


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

    def __unicode__(self):
        return self.titulo

    class Meta:
        ordering = ('ordem',)

