from __future__ import annotations
from typing import TYPE_CHECKING

from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from cards.cache import CACHE_CARDS_KEY, CACHE_SAVED_CARDS_KEY
from cards.models import Card
from cards.utils import get_card_ct_id
from interactions.models import Save

if TYPE_CHECKING:
    from typing import Type, Any


@receiver([post_delete, post_save], sender=Card)
def invalidate_cards(sender: Type[Card], instance: Card, **kwargs: Any) -> None:
    cache.delete(f"{CACHE_CARDS_KEY}{instance.module_id}")


@receiver([post_delete, post_save], sender=Save)
def invalidate_saved(sender: Type[Card], instance: Save, **kwargs: Any) -> None:
    if instance.content_type_id != get_card_ct_id():
        return
    cache.delete(f"{CACHE_SAVED_CARDS_KEY}{instance.user_id}")
