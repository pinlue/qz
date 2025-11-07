from __future__ import annotations

from typing import TYPE_CHECKING


from django.db.models import When, Case, Value, BooleanField

if TYPE_CHECKING:
    from django.contrib.auth.models import AnonymousUser
    from django.db.models import QuerySet
    from users.models import User


class BaseAnnotateRelationMixin:
    def _annotate_flag(
        self, user: User, field_name: str, related_name: str
    ) -> QuerySet:
        if not user.is_authenticated:
            return self.annotate(**{field_name: Value(False)})
        return self.annotate(
            **{
                field_name: Case(
                    When(**{f"{related_name}__user": user}, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            }
        )


class AnnotatePinnedMixin(BaseAnnotateRelationMixin):
    def with_ann_pinned(self, user: User | AnonymousUser) -> QuerySet:
        return self._annotate_flag(user, "pinned", "pins")


class AnnotateSavedMixin(BaseAnnotateRelationMixin):
    def with_ann_saved(self, user: User | AnonymousUser) -> QuerySet:
        return self._annotate_flag(user, "saved", "saves")
