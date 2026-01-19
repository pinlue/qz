from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import (
    Count,
    Q,
    Prefetch,
    Avg,
    Subquery,
    OuterRef,
    IntegerField,
    Value,
    DecimalField,
)
from django.db.models.functions import Coalesce

from common.permissions import get_accessible_q
from folders.models import Folder
from folders.service import FolderService
from modules.models import Module
from modules.service import ModuleService
from users.models import User

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest
    from rest_framework.request import Request


class UserRepository:
    @staticmethod
    def base_qs() -> QuerySet[User]:
        return User.objects.all()

    @staticmethod
    def with_public_counts(qs: QuerySet[User]) -> QuerySet[User]:
        return qs.annotate(
            public_modules_count=Count(
                "modules__id",
                filter=Q(modules__visible="public"),
                distinct=True,
            ),
            public_folders_count=Count(
                "folders__id",
                filter=Q(folders__visible="public"),
                distinct=True,
            ),
            total_cards_count=Count(
                "modules__cards__id",
                filter=Q(modules__visible="public"),
                distinct=True,
            ),
            avg_rate=Coalesce(
                Avg("modules__rates__rate", filter=Q(modules__visible="public")),
                Value(0.0),
                output_field=DecimalField(),
            ),
        )

    @staticmethod
    def with_prefetched_related(
        qs: QuerySet[User], request: Request | HttpRequest, user: User
    ) -> QuerySet[User]:
        modules_q = get_accessible_q(request, ModuleService.LIST_ACTION_CHAIN_LINKS)
        folders_q = get_accessible_q(request, FolderService.LIST_ACTION_CHAIN_LINKS)

        return qs.prefetch_related(
            Prefetch(
                "folders",
                queryset=Folder.objects.filter(folders_q)
                .annotate(
                    modules_count=Count("modules")
                )
                .with_ann_saved(user)
                .with_ann_pinned(user),
            ),
            Prefetch(
                "modules",
                queryset=Module.objects.filter(modules_q)
                .select_related("lang_from", "lang_to", "topic")
                .annotate(
                    avg_rate=Avg("rates__rate"),
                    cards_count=Count("cards"),
                )
                .with_ann_saved(user)
                .with_ann_pinned(user)
                .with_ann_perm(user)
                .prefetch_related("tags", "cards"),
            ),
        )

    @staticmethod
    def with_public_author_stats(qs: QuerySet[User]) -> QuerySet[User]:
        count_sq = Subquery(
            Module.objects.filter(user=OuterRef("pk"), visible="public")
            .values("user")
            .annotate(cnt=Count("id"))
            .values("cnt"),
            output_field=IntegerField(),
        )
        return (
            qs.annotate(
                public_modules_count=Coalesce(count_sq, Value(0)),
                avg_rate=Coalesce(
                    Avg("modules__rates__rate", filter=Q(modules__visible="public")),
                    Value(0.0),
                    output_field=DecimalField(),
                ),
            )
            .filter(public_modules_count__gt=0)
            .only("id", "username", "avatar", "email")
            .order_by("-avg_rate", "-public_modules_count")
        )
