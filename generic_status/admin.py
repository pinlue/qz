from django.contrib import admin

from generic_status.models import Learn, Rate, Perm


class RelatedAdminBase(admin.ModelAdmin):
    search_fields = ("user__username", "content_type__model")
    ordering = ("user",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "content_type")


@admin.register(Learn)
class LearnAdmin(RelatedAdminBase):
    list_filter = ("learned", "user")


@admin.register(Rate)
class RateAdmin(RelatedAdminBase):
    list_filter = ("rate", "user")


@admin.register(Perm)
class PermAdmin(RelatedAdminBase):
    list_filter = ("perm", "user")

