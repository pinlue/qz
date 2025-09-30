from django.db import models
from taggit.managers import TaggableManager


class Visibles(models.Model):
    class Status(models.TextChoices):
        Public = "public", "Public"
        Private = "private", "Private"

    visible = models.CharField(choices=Status.choices, default=Status.Public, max_length=7)

    class Meta:
        abstract = True


class Tags(models.Model):
    tags = TaggableManager()

    class Meta:
        abstract = True
