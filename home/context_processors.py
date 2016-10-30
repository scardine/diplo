from home.models import MenuItem, ConteudoRodape


def menu_context_processor(request):
    return {
        "top_menu": MenuItem.objects.all(),
        "conteudos_rodape": ConteudoRodape.objects.all(),
    }
