from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class ScheduledTask(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("done", "Done"),
        ("failed", "Failed"),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    name = models.CharField(max_length=255)
    kwargs = models.JSONField()
    scheduled_time = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} at {self.scheduled_time}"


class UserObjectRelation(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        unique_together = ("user", "content_type", "object_id")
        abstract = True
