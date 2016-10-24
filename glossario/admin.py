from django.contrib import admin

from glossario.models import Termo


class TermoAdmin(admin.ModelAdmin):
    search_fields = ('termo',)
    prepopulated_fields = {'slug', ('termo',)}

admin.site.register(Termo, TermoAdmin)