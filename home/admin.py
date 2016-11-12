from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from home.models import MenuItem, Conteudo, ConteudoRodape


class MenuAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


class ConteudoAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass

admin.site.register(MenuItem, MenuAdmin)
admin.site.register(Conteudo, ConteudoAdmin)
admin.site.register(ConteudoRodape, ConteudoAdmin)
