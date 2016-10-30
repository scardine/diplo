from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from glossario.models import Termo


class TermoList(ListView):
    model = Termo
    template_name = 'termo-list.html'

    def get_context_data(self, **kwargs):
        ctx = super(TermoList, self).get_context_data(**kwargs)
        slug_termo = self.kwargs.get('slug_termo')
        if slug_termo:
            ctx['termo'] = get_object_or_404(Termo, slug=slug_termo)
        else:
            ctx['termo'] = Termo.objects.first()
        return ctx
