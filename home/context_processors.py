from data.models import Tema, Categoria, Localidade, IndicadorFluxo
from home.models import MenuItem, ConteudoRodape


def menu_context_processor(request):
    return {
        "top_menu": MenuItem.objects.filter(depth=1),
        "conteudos_rodape": ConteudoRodape.objects.all(),
        "lista_categorias": Categoria.objects.filter(depth=1),
        "indicadores_fluxo": IndicadorFluxo.objects.all(),
    }
