from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import validate_deepl_key

from integration.models import DeepLApiKey


@receiver(post_save, sender=DeepLApiKey)
def trigger_deepl_validation(sender, instance, created, **kwargs):
    if instance.status == "PENDING":
        validate_deepl_key.delay(instance.id)