from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from languages.cache import CACHE_LANGUAGES_KEY
from languages.models import Language

if TYPE_CHECKING:
    from typing import Any, Type
    from django.db.models import Model


@receiver([post_save, post_delete], sender=Language)
def invalidate_languages_cache(
    sender: Type[Model], instance: Language, **kwargs: Any
) -> None:
    cache.delete(CACHE_LANGUAGES_KEY)
