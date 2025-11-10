from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from common.models import UserObjectRelation


class Pin(UserObjectRelation):
    pass


class Save(UserObjectRelation):
    pass


class Pinnable(models.Model):
    pins = GenericRelation("interactions.Pin")

    class Meta:
        abstract = True


class Savable(models.Model):
    saves = GenericRelation("interactions.Save")

    class Meta:
        abstract = True
