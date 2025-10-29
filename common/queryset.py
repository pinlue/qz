from django.db import models


def build_manager(*mixins):
    class DynamicQuerySet(*mixins, models.QuerySet):
        pass

    class DynamicManager(models.Manager.from_queryset(DynamicQuerySet)):
        pass

    return DynamicManager()