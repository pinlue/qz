from __future__ import annotations
from typing import TYPE_CHECKING

import django_filters
from django.db.models import Q, Count
from django_filters import rest_framework as filters

from modules.models import Module

if TYPE_CHECKING:
    from django.db.models import QuerySet


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class ModuleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    description = django_filters.CharFilter(
        field_name="description", lookup_expr="icontains"
    )

    lang_to = django_filters.NumberFilter(field_name="lang_to_id")
    lang_from = django_filters.NumberFilter(field_name="lang_from_id")
    topic = django_filters.NumberFilter(field_name="topic_id")
    cards_count__gt = django_filters.NumberFilter(
        field_name="cards_count", lookup_expr="gt"
    )
    cards_count__lt = django_filters.NumberFilter(
        field_name="cards_count", lookup_expr="lt"
    )

    tags = CharInFilter(method="filter_tags")

    ordering = django_filters.OrderingFilter(
        fields=(
            ("name", "name"),
            ("created", "created"),
        )
    )

    class Meta:
        model = Module
        fields = [
            "name",
            "description",
            "lang_to",
            "lang_from",
            "topic",
            "tags",
        ]

    def filter_tags(
        self, queryset: QuerySet[Module], name: str, value: list[str]
    ) -> QuerySet[Module]:
        if not value:
            return queryset
        return (
            queryset.annotate(
                matching_tags_count=Count(
                    "tags",
                    filter=Q(tags__name__in=value),
                    distinct=True,
                )
            )
            .filter(matching_tags_count__gt=0)
            .order_by("-matching_tags_count")
        )
