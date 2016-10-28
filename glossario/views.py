from django.views.generic import ListView
from glossario.models import Termo


class TermoList(ListView):
    model = Termo
    template_name = 'termo-list.html'