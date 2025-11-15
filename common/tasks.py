from celery import shared_task
from celery_singleton import Singleton
from django.db import transaction
from django.utils import timezone
from celery import current_app

from common.models import ScheduledTask


@shared_task(base=Singleton)
def run_scheduled_tasks() -> None:
    now = timezone.now()
    with transaction.atomic():
        due_tasks = (
            ScheduledTask.objects
            .select_for_update(skip_locked=True)
            .filter(status="pending", scheduled_time__lte=now)
        )
        for task in due_tasks:
            try:
                current_app.send_task(task.name, kwargs=task.kwargs)
                task.delete()
            except Exception:
                task.status = "failed"
                task.save(update_fields=["status"])
