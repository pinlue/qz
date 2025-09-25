from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import User
from .tasks import delete_avatar_file


@receiver(post_delete, sender=User)
def user_post_delete(sender, instance, **kwargs):
    if instance.avatar:
        delete_avatar_file.delay(instance.avatar.path)