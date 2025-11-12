from django.contrib import admin
from django.db.models import Count

from topics.models import Topic


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("name", "modules_count")
    search_fields = ("name",)
    ordering = ("name",)
    fields = ("name",)
    readonly_fields = ("modules_count",)
    list_per_page = 50

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_modules_count=Count("modules", distinct=True))

    def modules_count(self, obj):
        return getattr(obj, "_modules_count", 0)
