from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models, transaction
from rest_framework.exceptions import ValidationError

from abstracts.models import Tag, Visible
from common.queryset import build_manager
from generic_status.models import Permable, Rateable
from generic_status.queryset import AnnotatePermMixin, AnnotateRatedMixin
from interactions.models import Savable, Pinnable
from interactions.queryset import AnnotateSavedMixin, AnnotatePinnedMixin
from users.models import User

if TYPE_CHECKING:
    from typing import Any


class Module(Tag, Visible, Savable, Pinnable, Permable, Rateable, models.Model):
    objects = build_manager(
        AnnotateSavedMixin, AnnotatePinnedMixin, AnnotatePermMixin, AnnotateRatedMixin
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="modules")
    topic = models.ForeignKey(
        "topics.Topic", on_delete=models.CASCADE, related_name="modules"
    )
    lang_from = models.ForeignKey(
        "languages.Language", on_delete=models.CASCADE, related_name="modules_from_lang"
    )
    lang_to = models.ForeignKey(
        "languages.Language", on_delete=models.CASCADE, related_name="modules_to_lang"
    )

    folders = models.ManyToManyField("folders.Folder", related_name="modules")

    class Meta:
        ordering = ["name"]

    def clean(self) -> None:
        if self.lang_from == self.lang_to:
            raise ValidationError("Source and target languages must be different")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    def copy(self, new_user: User) -> None:
        from cards.models import Card

        with transaction.atomic():
            new_module = Module.objects.create(
                name=self.name,
                user=new_user,
                topic=self.topic,
                lang_from=self.lang_from,
                lang_to=self.lang_to,
            )

            cards_bulk = [
                Card(
                    module=new_module,
                    original=card.original,
                    translation=card.translation,
                )
                for card in self.cards.all()
            ]

            if cards_bulk:
                Card.objects.bulk_create(cards_bulk)
