from __future__ import annotations
from typing import TYPE_CHECKING

from django.db.models import Count, Q, Prefetch, Avg

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
