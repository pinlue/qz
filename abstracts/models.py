from django.db import models
from taggit.managers import TaggableManager


class Visible(models.Model):
    class Status(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"

    visible = models.CharField(choices=Status.choices, default=Status.PUBLIC, max_length=7)

    class Meta:
        abstract = True


class Tag(models.Model):
    tags = TaggableManager()

    class Meta:
        abstract = True
