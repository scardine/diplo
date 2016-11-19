from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from home.models import MenuItem, Conteudo, ConteudoRodape


class MenuAdmin(TreeAdmin):
    form = movenodeform_factory(MenuItem)


class ConteudoAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass

admin.site.register(MenuItem, MenuAdmin)
admin.site.register(Conteudo, ConteudoAdmin)
admin.site.register(ConteudoRodape, ConteudoAdmin)
