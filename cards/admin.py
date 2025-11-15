from django.contrib import admin

from cards.models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("original", "translation", "module", "created",)
    search_fields = ("original", "translation")
    ordering = ("original",)
    list_select_related = ("module", "module__user")
    raw_id_fields = ("module",)
