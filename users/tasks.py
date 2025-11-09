import os

from celery import shared_task


@shared_task
def delete_avatar_file(path: str) -> None:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Avatar file not found: {path}")
    os.remove(path)
