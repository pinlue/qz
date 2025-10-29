from django.core import validators
from django.db import models

from abstracts.models import Visible
from common.queryset import build_manager
from interactions.models import Savable, Pinnable
from interactions.queryset import AnnotateSavedMixin, AnnotatePinnedMixin
from users.models import User


class Folder(Visible, Savable, Pinnable, models.Model):
    objects = build_manager(AnnotateSavedMixin, AnnotatePinnedMixin)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')

    name = models.CharField(max_length=255)
    color = models.CharField(
        max_length=7,
        validators=[
            validators.RegexValidator(
                regex=r'^#[0-9A-Fa-f]{6}$',
                message='Color must be a valid hex code, e.g. #A1B2C3'
            )
        ]
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
