from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from topics.cache import CACHE_TOPICS_KEY
from topics.models import Topic

if TYPE_CHECKING:
    from typing import Any, Type
    from django.db.models import Model


@receiver([post_save, post_delete], sender=Topic)
def invalidate_topics_cache(
    sender: Type[Model], instance: Topic, **kwargs: Any
) -> None:
    cache.delete(CACHE_TOPICS_KEY)