from celery import shared_task
import os


@shared_task
def delete_avatar_file(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Avatar file not found: {path}")
    os.remove(path)