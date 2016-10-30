# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.utils.six import python_2_unicode_compatible


@python_2_unicode_compatible
class MenuItem(models.Model):
    ordem = models.PositiveIntegerField(default=0)
    label = models.CharField(max_length=60)
    url = models.CharField(max_length=200)

    class Meta:
        verbose_name = u"Ítem de menu"
        verbose_name_plural = u"Ítens de menu"
        ordering = ('ordem',)

    def __str__(self):
        return self.label


@python_2_unicode_compatible
class Conteudo(models.Model):
    TIPO = (
        ('html', 'HTML'),
        ('markdown', 'Markdown'),
    )
    ordem = models.PositiveIntegerField(default=1)
    tipo = models.CharField(max_length=30, default='html', choices=TIPO)
    css = models.CharField(max_length=100, blank=True, null=True)
    corpo = models.TextField()

    class Meta:
        ordering = ('ordem',)

    def __str__(self):
        return "Conteudo Home {}".format(self.ordem)


@python_2_unicode_compatible
class ConteudoRodape(models.Model):
    TIPO = (
        ('html', 'HTML'),
        ('markdown', 'Markdown'),
    )
    ordem = models.PositiveIntegerField(default=1)
    tipo = models.CharField(max_length=30, default='html', choices=TIPO)
    css = models.CharField(max_length=100, blank=True, null=True)
    corpo = models.TextField()

    class Meta:
        ordering = ('ordem',)

    def __str__(self):
        return "Conteudo Rodapé {}".format(self.ordem)
