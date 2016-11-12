from django.contrib.flatpages.models import FlatPage
from django.views.generic import TemplateView

from data.models import Categoria
from home.models import Conteudo


class Index(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        d = super(Index, self).get_context_data(**kwargs)
        d['categorias'] = Categoria.objects.filter(depth=1, home=True).exclude(slug='fluxos-dos-servicos-de-saude').order_by('ordem')
        d['conteudo_home'] = FlatPage.objects.get(url='/conteudo/home/').content
        d['conteudos'] = Conteudo.objects.all()
        d['fluxos'] = Categoria.objects.get(slug='fluxos-dos-servicos-de-saude')
        return d


