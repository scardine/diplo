# coding=utf-8
from django import forms

from data.models import Tema, Localidade, Dashboard


class TemaLocalForm(forms.Form):
    tema = forms.ModelChoiceField(queryset=Tema.objects.filter(dashboard=True), label=u'Escolha um tema', widget=forms.Select(attrs={"onchange":'recarrega(this)'}))
    localidades = forms.ChoiceField(choices=Localidade.TIPO, label=u'Regionalização', widget=forms.Select(attrs={"onchange":'recarrega(this)'}))


class DashboardLocalForm(forms.Form):
    dashboard = forms.ModelChoiceField(queryset=Dashboard.objects.all(), label=u'Painel temático', widget=forms.Select(attrs={"onchange":'recarrega(this)'}))
    localidades = forms.ChoiceField(choices=Localidade.TIPO, label=u'Regionalização', widget=forms.Select(attrs={"onchange":'recarrega(this)'}))
