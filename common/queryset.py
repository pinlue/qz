from typing import Any

from django.db import models


def build_manager(*mixins: type[Any]) -> models.Manager:
    class DynamicQuerySet(*mixins, models.QuerySet):
        pass

    class DynamicManager(models.Manager.from_queryset(DynamicQuerySet)):
        pass

    return DynamicManager()  # type: ignore[misc]
