from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from data.models import Fonte, Tema, Indicador, Dashboard, Painel, Modelo


class TemaAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('nome',)


class FonteAdmin(admin.ModelAdmin):
    list_display = ('nome',)


class IndicadorAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    list_filter = ('tema',)
    ordering = ('tema', 'nome',)


class PainelInline(SortableInlineAdminMixin, admin.StackedInline):
    model = Painel


class DashboardAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = (PainelInline,)
    search_fields = ('titulo',)


admin.site.register(Tema, TemaAdmin)
admin.site.register(Fonte, FonteAdmin)
admin.site.register(Indicador, IndicadorAdmin)
admin.site.register(Dashboard, DashboardAdmin)
admin.site.register(Modelo)

