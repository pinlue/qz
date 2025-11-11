from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Count, Prefetch, QuerySet

from cards.models import Card
from common.access_chain import AccessibleChain
from common.permissions import get_accessible_q
from modules.models import Module

if TYPE_CHECKING:
    from users.models import User
    from typing import Type
    from rest_framework.request import Request


class ModuleRepository:
    @staticmethod
    def base_qs() -> QuerySet[Module]:
        return Module.objects.select_related(
            "user", "topic", "lang_from", "lang_to"
        ).annotate(cards_count=Count("cards"))

    @staticmethod
    def with_cards_and_annotations(
        qs: QuerySet[Module], user: User
    ) -> QuerySet[Module]:
        return (
            qs.prefetch_related(
                Prefetch(
                    "cards",
                    queryset=Card.objects.all()
                    .with_ann_saved(user)
                    .with_ann_learned(user),
                ),
            )
            .with_ann_saved(user)
            .with_ann_pinned(user)
            .with_ann_rate(user)
            .with_ann_perm(user)
        )

    @staticmethod
    def accessible_for_user(
        qs: QuerySet[Module], request: Request, chain_links: list[Type[AccessibleChain]]
    ) -> QuerySet[Module]:
        return qs.filter(get_accessible_q(request, chain_links))
