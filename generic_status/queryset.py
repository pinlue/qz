from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Case, When, F, Value, CharField, IntegerField

if TYPE_CHECKING:
    from django.db.models import Field, QuerySet
    from users.models import User


class BaseAnnotateRelationMixin:
    def _annotate_relation(
        self,
        user: User,
        field_name: str,
        related_name: str,
        value_field: str,
        output_field: Field,
    ) -> QuerySet:
        if not user.is_authenticated:
            return self.annotate(**{field_name: Value("")})
        return self.annotate(
            **{
                field_name: Case(
                    When(
                        **{f"{related_name}__user": user},
                        then=F(f"{related_name}__{value_field}"),
                    ),
                    default=Value(None),
                    output_field=output_field,
                )
            }
        )


class AnnotateLearnedMixin(BaseAnnotateRelationMixin):
    def with_ann_learned(self, user: User) -> QuerySet:
        return self._annotate_relation(
            user=user,
            field_name="learned_status",
            related_name="learns",
            value_field="learned",
            output_field=CharField(),
        )


class AnnotateRatedMixin(BaseAnnotateRelationMixin):
    def with_ann_rate(self, user: User) -> QuerySet:
        return self._annotate_relation(
            user=user,
            field_name="user_rate",
            related_name="rates",
            value_field="rate",
            output_field=IntegerField(),
        )


class AnnotatePermMixin(BaseAnnotateRelationMixin):
    def with_ann_perm(self, user: User) -> QuerySet:
        return self._annotate_relation(
            user=user,
            field_name="user_perm",
            related_name="perms",
            value_field="perm",
            output_field=CharField(),
        )
