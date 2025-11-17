from django.core.cache import cache

from cards.cache import (
    CACHE_CARDS_TTL,
    CACHE_SAVED_CARDS_TTL,
    CACHE_CARDS_KEY,
    CACHE_SAVED_CARDS_KEY,
)
from cards.models import Card
from cards.utils import get_card_ct_id
from interactions.models import Save


class CardRepository:
    @staticmethod
    def get_cached_cards(module_id: int) -> list[dict]:
        key = f"{CACHE_CARDS_KEY}{module_id}"
        cards = cache.get(key)

        if cards is not None:
            return cards

        qs = Card.objects.filter(module_id=module_id).order_by("original")
        cards = list(qs.values("id", "original", "translation", "module_id"))

        cache.set(key, cards, CACHE_CARDS_TTL)
        return cards

    @staticmethod
    def get_cached_saved_ids(user_id: int) -> set[int]:
        key = f"{CACHE_SAVED_CARDS_KEY}{user_id}"
        saved_ids = cache.get(key)

        if saved_ids is not None:
            return set(saved_ids)

        saved_ids = list(
            Save.objects.filter(
                user_id=user_id,
                content_type=get_card_ct_id(),
            ).values_list("object_id", flat=True)
        )

        cache.set(key, saved_ids, CACHE_SAVED_CARDS_TTL)
        return set(saved_ids)
