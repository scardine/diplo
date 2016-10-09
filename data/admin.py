from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from data.models import Fonte, Tema, Indicador, Dashboard, Painel, Modelo, Localidade


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


class PainelInline(SortableInlineAdminMixin, admin.StackedInline):
    model = Painel


class DashboardAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = (PainelInline,)
    search_fields = ('titulo',)


class LocalidadeAdmin(admin.ModelAdmin):
    search_fields = ('nome', 'codigo',)
    list_display = ('nome',)
    list_filter = ('tipo',)


admin.site.register(Tema, TemaAdmin)
admin.site.register(Fonte, FonteAdmin)
admin.site.register(Indicador, IndicadorAdmin)
admin.site.register(Dashboard, DashboardAdmin)
admin.site.register(Modelo)
admin.site.register(Localidade, LocalidadeAdmin)
