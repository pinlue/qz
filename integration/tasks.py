from celery import shared_task
import deepl
from .models import DeepLApiKey


@shared_task
def validate_deepl_key(key_id: int):
    try:
        deepl_key = DeepLApiKey.objects.get(id=key_id)

        translator = deepl.Translator(deepl_key.api_key)

        usage = translator.get_usage()

        if usage.character.limit > 0:
            deepl_key.status = "ACCEPTED"
        else:
            deepl_key.status = "REJECTED"

    except Exception:
        deepl_key.status = "REJECTED"

    deepl_key.save()