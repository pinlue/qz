from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.db.models import Subquery, OuterRef, Value, CharField, IntegerField

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from users.models import User


class AnnotateLearnedMixin:
    def with_ann_learned(self, user: User) -> QuerySet:
        from generic_status.models import Learn

        if not user.is_authenticated:
            return self.annotate(learned_status=Value("", output_field=CharField()))

        return self.annotate(
            learned_status=Subquery(
                Learn.objects.filter(
                    content_type=ContentType.objects.get_for_model(self.model),
                    object_id=OuterRef("pk"),
                    user=user,
                ).values("learned")[:1],
                output_field=CharField(),
            )
        )


class AnnotateRatedMixin:
    def with_ann_rate(self, user: User) -> QuerySet:
        from generic_status.models import Rate

        if not user.is_authenticated:
            return self.annotate(user_rate=Value(None, output_field=IntegerField()))

        return self.annotate(
            user_rate=Subquery(
                Rate.objects.filter(
                    content_type=ContentType.objects.get_for_model(self.model),
                    object_id=OuterRef("pk"),
                    user=user,
                ).values("rate")[:1],
                output_field=IntegerField(),
            )
        )


class AnnotatePermMixin:
    def with_ann_perm(self, user: User) -> QuerySet:
        from generic_status.models import Perm

        if not user.is_authenticated:
            return self.annotate(user_perm=Value("", output_field=CharField()))

        return self.annotate(
            user_perm=Subquery(
                Perm.objects.filter(
                    content_type=ContentType.objects.get_for_model(self.model),
                    object_id=OuterRef("pk"),
                    user=user,
                ).values("perm")[:1],
                output_field=CharField(),
            )
        )
