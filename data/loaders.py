from django.template import Origin
from django.template import TemplateDoesNotExist
from django.template.loaders.base import Loader

from data.models import Modelo


class ModeloLoader(Loader):
    def get_contents(self, origin):
        try:
            modelo = Modelo.objects.get(pk=origin.name)
        except Modelo.DoesNotExist:
            raise TemplateDoesNotExist, origin.template_name
        return modelo.html

    def get_template_sources(self, template_name):
        if ':' not in template_name:
            return
        name = template_name.split(':')[-1]
        yield Origin(name, template_name, self)

