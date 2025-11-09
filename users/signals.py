from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import User
from .tasks import delete_avatar_file

if TYPE_CHECKING:
    from typing import Any, Type


@receiver(post_delete, sender=User)
def user_post_delete(sender: Type[User], instance: User, **kwargs: Any) -> None:
    if instance.avatar:
        delete_avatar_file.delay(instance.avatar.path)
