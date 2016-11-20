from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from data.models import Fonte, Tema, Indicador, Dashboard, Painel, Modelo, Localidade, Categoria, IndicadorFluxo


class TemaAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('nome', 'dashboard')
    list_editable = ('dashboard',)


class FonteAdmin(admin.ModelAdmin):
    list_display = ('nome',)


class IndicadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tema',)
    list_filter = ('tema',)
    search_fields = ('nome', 'descricao', 'observacao',)
    ordering = ('tema', 'nome',)


class IndicadorFluxoAdmin(admin.ModelAdmin):
    list_display = ('subgrupo', 'complexidade', 'especialidade')
    list_filter = ('complexidade', 'especialidade')
    search_fields = ('subgrupo',)
    ordering = ('subgrupo',)


class PainelInline(SortableInlineAdminMixin, admin.StackedInline):
    model = Painel


class DashboardAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = (PainelInline,)
    search_fields = ('titulo',)
    prepopulated_fields = {
        'slug': ('titulo',),
    }


class LocalidadeAdmin(admin.ModelAdmin):
    search_fields = ('nome', 'codigo',)
    list_display = ('nome',)
    list_filter = ('tipo',)


class CategoriaAdmin(TreeAdmin):
    form = movenodeform_factory(Categoria)
    list_display = ('nome', 'home', 'menu',)
    list_editable = ('home', 'menu',)


admin.site.register(Tema, TemaAdmin)
admin.site.register(Fonte, FonteAdmin)
admin.site.register(Indicador, IndicadorAdmin)
admin.site.register(IndicadorFluxo, IndicadorFluxoAdmin)
admin.site.register(Dashboard, DashboardAdmin)
admin.site.register(Modelo)
admin.site.register(Localidade, LocalidadeAdmin)
admin.site.register(Categoria, CategoriaAdmin)