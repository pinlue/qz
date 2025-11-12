from django.db import models

from common.queryset import build_manager
from generic_status.models import Learnable
from generic_status.queryset import AnnotateLearnedMixin
from interactions.models import Savable
from interactions.queryset import AnnotateSavedMixin


class Card(Savable, Learnable, models.Model):
    objects = build_manager(AnnotateSavedMixin, AnnotateLearnedMixin)

    original = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)

    created = models.DateTimeField(auto_now_add=True)

    module = models.ForeignKey(
        "modules.Module", on_delete=models.CASCADE, related_name="cards"
    )

    class Meta:
        ordering = ["original"]
        unique_together = ("original", "translation", "module")

    def __str__(self) -> str:
        return f"{self.original} - {self.translation}"
