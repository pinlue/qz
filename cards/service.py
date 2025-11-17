from __future__ import annotations

from typing import TYPE_CHECKING

from cards.repository import CardRepository

if TYPE_CHECKING:
    from django.contrib.auth.models import AnonymousUser
    from users.models import User


class CardService:
    @staticmethod
    def get_cards_with_saved(module_id: int, user: User | AnonymousUser) -> list[dict]:
        cards = CardRepository.get_cached_cards(module_id)

        if user.is_authenticated:
            saved_ids = CardRepository.get_cached_saved_ids(user.id)
        else:
            saved_ids = set()

        return [{**card, "saved": card["id"] in saved_ids} for card in cards]
