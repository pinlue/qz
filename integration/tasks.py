from celery import shared_task
import deepl
from django.db import transaction

from .models import DeepLApiKey


@shared_task
def validate_deepl_key(key_id: int) -> None:
    with transaction.atomic():
        try:
            deepl_key = DeepLApiKey.objects.select_for_update().get(id=key_id)
        except DeepLApiKey.DoesNotExist:
            return

        if deepl_key.status != DeepLApiKey.Status.PENDING:
            return

        try:
            translator = deepl.Translator(deepl_key.api_key)
            usage = translator.get_usage()

            if usage.character.limit is None or usage.character.count < usage.character.limit:
                deepl_key.status = DeepLApiKey.Status.ACCEPTED
            else:
                deepl_key.status = DeepLApiKey.Status.REJECTED
        except (deepl.exceptions.AuthorizationException,
                deepl.exceptions.QuotaExceededException,
                deepl.exceptions.DeepLException):
            deepl_key.status = DeepLApiKey.Status.REJECTED

        deepl_key.save(update_fields=["status"])
