from functools import lru_cache

from django.contrib.contenttypes.models import ContentType

from cards.models import Card


@lru_cache
def get_card_ct_id() -> int:
    return ContentType.objects.get_for_model(Card).id