from __future__ import annotations

from typing import TYPE_CHECKING

from common.permissions import get_accessible_q
from folders.models import Folder
from modules.models import Module
from django.db.models import Count, Q, Prefetch

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request
    from typing import Type
    from common.access_chain import AccessibleChain
    from users.models import User


class FolderRepository:
    @staticmethod
    def base_qs() -> QuerySet[Folder]:
        return Folder.objects.select_related("user")

    @staticmethod
    def with_modules_count(qs: QuerySet[Folder], modules_q: Q) -> QuerySet[Folder]:
        return qs.annotate(
            modules_count=Count(
                "modules",
                filter=Q(modules__in=Module.objects.filter(modules_q)),
                distinct=True,
            )
        )

    @staticmethod
    def accessible_for_user(
        qs: QuerySet[Folder], request: Request, chain_links: list[Type[AccessibleChain]]
    ) -> QuerySet[Folder]:
        return qs.filter(get_accessible_q(request=request, links=chain_links))

    @staticmethod
    def with_modules_prefetched(
        qs: QuerySet[Folder], user: User, modules_q: Q
    ) -> QuerySet[Folder]:
        return (
            qs.prefetch_related(
                Prefetch(
                    "modules",
                    queryset=Module.objects.filter(modules_q)
                    .select_related("user", "topic", "lang_from", "lang_to")
                    .with_ann_saved(user)
                    .with_ann_pinned(user)
                    .with_ann_perm(user),
                )
            )
            .with_ann_saved(user)
            .with_ann_pinned(user)
        )
