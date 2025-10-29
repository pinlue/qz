from django.db.models import Case, When, F, Value, CharField, IntegerField


class BaseAnnotateRelationMixin:
    def _annotate_relation(self, user, field_name, related_name, value_field, output_field):
        return self.annotate(
            **{
                field_name: Case(
                    When(
                        **{f"{related_name}__user": user},
                        then=F(f"{related_name}__{value_field}")
                    ),
                    default=Value(None),
                    output_field=output_field,
                )
            }
        )


class AnnotateLearnedMixin(BaseAnnotateRelationMixin):
    def with_ann_learned(self, user):
        return self._annotate_relation(
            user=user,
            field_name="learned_status",
            related_name="learns",
            value_field="learned",
            output_field=CharField(),
        )


class AnnotateRatedMixin(BaseAnnotateRelationMixin):
    def with_ann_rate(self, user):
        return self._annotate_relation(
            user=user,
            field_name="user_rate",
            related_name="rates",
            value_field="rate",
            output_field=IntegerField(),
        )


class AnnotatePermMixin(BaseAnnotateRelationMixin):
    def with_ann_perm(self, user):
        return self._annotate_relation(
            user=user,
            field_name="user_perm",
            related_name="perms",
            value_field="perm",
            output_field=CharField(),
        )
