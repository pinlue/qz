from celery import shared_task
from django.utils import timezone
from celery import current_app

from common.models import ScheduledTask


@shared_task
def run_scheduled_tasks():
    now = timezone.now()
    due_tasks = ScheduledTask.objects.filter(status="pending", scheduled_time__lte=now)
    for task in due_tasks:
        try:
            current_app.send_task(task.name, kwargs=task.kwargs)
            task.delete()
        except Exception as _:
            task.status = "failed"
            task.save(update_fields=["status"])
