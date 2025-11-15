from django.contrib import admin

from interactions.models import Pin, Save


class InteractionsAdminBase(admin.ModelAdmin):
    list_filter = ("user", "content_type")
    search_fields = ("user__username", "content_type__model")
    ordering = ("user",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "content_type")


@admin.register(Pin)
class PinAdmin(InteractionsAdminBase):
    pass


@admin.register(Save)
class SaveAdmin(InteractionsAdminBase):
    pass
