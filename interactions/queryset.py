from django.db.models import When, Case, Value, BooleanField


class BaseAnnotateRelationMixin:
    def _annotate_flag(self, user, field_name, related_name):
        return self.annotate(
            **{
                field_name: Case(
                    When(
                        **{f"{related_name}__user": user},
                        then=Value(True)
                    ),
                    default=Value(False),
                    output_field=BooleanField()
                )
            }
        )


class AnnotatePinnedMixin(BaseAnnotateRelationMixin):
    def with_ann_pinned(self, user):
        return self._annotate_flag(user, "pinned", "pins")


class AnnotateSavedMixin(BaseAnnotateRelationMixin):
    def with_ann_saved(self, user):
        return self._annotate_flag(user, "saved", "saves")
