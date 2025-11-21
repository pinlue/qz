from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin
from django.db.models import Count, Prefetch

from modules.models import Module
from .models import Folder

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request
    from django.http import HttpRequest


class FolderModulesInline(admin.TabularInline):
    model = Folder.modules.through
    extra = 0
    verbose_name = "Module"
    verbose_name_plural = "Modules"
    fields = ("module_name",)
    raw_id_fields = ("module",)
    readonly_fields = ("module_name",)

    can_delete = False
    max_num = 0
    show_change_link = False

    def has_add_permission(self, request: Request, obj=None) -> bool:
        return False

    def has_change_permission(self, request: Request, obj=None) -> bool:
        return False

    def get_queryset(self, request: Request | HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("module")

    def module_name(self, obj) -> str:
        return obj.module.name

    module_name.short_description = "Module"


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "modules_count")
    search_fields = ("name",)
    list_filter = ("user",)
    ordering = ("name",)
    readonly_fields = ("modules_count",)
    raw_id_fields = ("user",)
    list_per_page = 50
    inlines = [FolderModulesInline]

    def get_queryset(self, request: Request | HttpRequest) -> QuerySet:
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            Prefetch(
                "modules",
                queryset=Module.objects.only("id", "name"),
                to_attr="prefetched_modules",
            )
        ).annotate(modules_count=Count("modules", distinct=True))

    @admin.display(description="Modules Count", ordering="modules_count")
    def modules_count(self, obj) -> int:
        return obj.modules_count
