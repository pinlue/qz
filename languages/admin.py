from django.contrib import admin
from django.db.models import Count

from languages.models import Language


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "modules_from_lang_count", "modules_to_lang_count")
    search_fields = ("name", "code")
    ordering = ("name",)
    fields = ("name", "code", "flag")
    list_per_page = 30

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            from_count=Count("modules_from_lang", distinct=True),
            to_count=Count("modules_to_lang", distinct=True),
        )

    @admin.display(description="From Lang Modules", ordering="from_count")
    def modules_from_lang_count(self, obj):
        return obj.from_count

    @admin.display(description="To Lang Modules", ordering="to_count")
    def modules_to_lang_count(self, obj):
        return obj.to_count
