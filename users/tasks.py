import os

from celery import shared_task


@shared_task
def delete_avatar_file(path: str) -> None:
    try:
        if os.path.isfile(path):
            os.remove(path)
    except Exception as e:
        pass
