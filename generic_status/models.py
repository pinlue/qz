from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from common.models import UserObjectRelation


class Learn(UserObjectRelation):
    class Status(models.TextChoices):
        LEARNED = "learned", "Learned"
        IN_PROGRESS = "in_progress", "In progress"
    learned = models.CharField(max_length=11, choices=Status.choices)


class Rate(UserObjectRelation):
    class Status(models.IntegerChoices):
        ONE = 1, "1"
        TWO = 2, "2"
        THREE = 3, "3"
        FOUR = 4, "4"
        FIVE = 5, "5"
    rate = models.IntegerField(choices=Status.choices)


class Perm(UserObjectRelation):
    class Status(models.TextChoices):
        EDITOR = "editor", "Editor"
        VIEWER = "viewer", "Viewer"
    perm = models.CharField(max_length=6, choices=Status.choices)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id', 'perm')


class Learnable(models.Model):
    learns = GenericRelation("generic_status.Learn")

    class Meta:
        abstract = True


class Rateable(models.Model):
    rates = GenericRelation("generic_status.Rate")

    class Meta:
        abstract = True


class Permable(models.Model):
    perms = GenericRelation("generic_status.Perm")

    class Meta:
        abstract = True