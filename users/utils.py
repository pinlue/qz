from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from users.models import User


def user_avatar_path(instance: User, filename: str) -> str:
    ext = filename.split(".")[-1]
    filename = f"user_{instance.pk}.{ext}"
    return os.path.join("avatars", filename)
