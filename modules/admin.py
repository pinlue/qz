from django.contrib import admin
from django.db.models import Count

from cards.models import Card
from modules.models import Module


class CardInline(admin.TabularInline):
    model = Card
    extra = 0
    fields = ("original", "translation", "created")
    readonly_fields = ("created",)
    ordering = ("original",)
    show_change_link = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.only("id", "original", "translation", "created", "module_id")


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "topic",
        "lang_from",
        "lang_to",
        "folders_count",
        "cards_count",
        "created",
        "visible",
    )
    list_select_related = (
        "topic",
        "lang_from",
        "lang_to",
        "user",
    )
    list_filter = ("visible",)
    list_editable = ("visible",)
    search_fields = ("name", "description")
    readonly_fields = ("created", "folders_count", "cards_count")
    raw_id_fields = (
        "user",
        "topic",
        "lang_from",
        "lang_to",
    )
    list_per_page = 50
    inlines = [CardInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            folders_count=Count("folders", distinct=True),
            cards_count=Count("cards", distinct=True),
        )

    @admin.display(description="Folders Count", ordering="folders_count")
    def folders_count(self, obj):
        return obj.folders_count

    @admin.display(description="Cards Count", ordering="cards_count")
    def cards_count(self, obj):
        return obj.cards_count
