# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django_pandas.io import read_frame


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
    ordem = models.IntegerField(default=1)

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


class Pipeline(models.Model):
    nome = models.CharField(max_length=200)
    filtros = models.TextField(null=True, blank=True)
    transforms = models.TextField(u"Transformações", null=True, blank=True)
    ordens = models.TextField(u'Ordenação', null=True, blank=True)




