from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


class ScheduledTask(models.Model):
    name = models.CharField(max_length=255)
    kwargs = models.JSONField()
    scheduled_time = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    @classmethod
    def reschedule_tasks(cls, only_failed=False):
        if only_failed:
            cls.objects.filter(status='failed').update(status='pending')
        else:
            now = timezone.now()
            cls.objects.all().update(status='pending', scheduled_time=now)

    def __str__(self):
        return f"{self.name} at {self.scheduled_time}"


class UserObjectRelation(models.Model):
    user_related_name = None

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        abstract = True