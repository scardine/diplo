from django.contrib import admin

from data.models import Fonte, Tema, Indicador


class TemaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem')
    list_editable = ('ordem',)


class FonteAdmin(admin.ModelAdmin):
    list_display = ('nome',)


class IndicadorAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    list_filter = ('tema',)
    ordering = ('tema', 'nome',)


admin.site.register(Tema, TemaAdmin)
admin.site.register(Fonte, FonteAdmin)
admin.site.register(Indicador, IndicadorAdmin)
