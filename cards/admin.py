from django.contrib import admin

from cards.models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("original", "translation", "module", "created", "module_user")
    search_fields = ("original", "translation", "module__name", "module__user__username")
    list_filter = ("module__user", "module", "created")
    ordering = ("original",)
    list_select_related = ("module", "module__user")
    raw_id_fields = ("module",)

    def module_user(self, obj):
        return obj.module.user

    module_user.short_description = "User"
    module_user.admin_order_field = "module__user"
