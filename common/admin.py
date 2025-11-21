from django.contrib import admin

from common.models import ScheduledTask


@admin.register(ScheduledTask)
class ScheduledTaskAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "status",
        "scheduled_time",
        "created",
        "short_kwargs",
    )
    list_filter = ("status", "scheduled_time", "created")
    list_editable = ("status",)
    search_fields = ("name", "kwargs")
    ordering = ("-scheduled_time",)
    readonly_fields = ("created",)

    def short_kwargs(self, obj: ScheduledTask) -> str:
        text = str(obj.kwargs)
        return text if len(text) < 60 else text[:57] + "..."

    short_kwargs.short_description = "Kwargs"


