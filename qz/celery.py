import os
from celery import app as celery_app
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qz.settings")
app = celery_app.Celery("qz")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "run-scheduled-tasks-every-minute": {
        "task": "common.tasks.run_scheduled_tasks",
        "schedule": crontab(minute="*"),
    },
}
