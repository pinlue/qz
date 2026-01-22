from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists, OuterRef, Value, BooleanField

if TYPE_CHECKING:
    from django.contrib.auth.models import AnonymousUser
    from django.db.models import QuerySet
    from users.models import User



class AnnotatePinnedMixin:
    def with_ann_pinned(self, user: User | AnonymousUser) -> QuerySet:
        from interactions.models import Pin

        if not user.is_authenticated:
            return self.annotate(pinned=Value(False, output_field=BooleanField()))

        return self.annotate(
            pinned=Exists(
                Pin.objects.filter(
                    object_id=OuterRef("pk"),
                    content_type__model=ContentType.objects.get_for_model(self.model),
                    user=user
                )
            )
        )


class AnnotateSavedMixin:
    def with_ann_saved(self, user: User | AnonymousUser) -> QuerySet:
        from interactions.models import Save

        if not user.is_authenticated:
            return self.annotate(saved=Value(False, output_field=BooleanField()))

        return self.annotate(
            saved=Exists(
                Save.objects.filter(
                    object_id=OuterRef("pk"),
                    content_type__model=ContentType.objects.get_for_model(self.model),
                    user=user
                )
            )
        )