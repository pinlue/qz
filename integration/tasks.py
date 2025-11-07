from celery import shared_task
import deepl
from .models import DeepLApiKey


@shared_task
def validate_deepl_key(key_id: int) -> None:
    try:
        deepl_key = DeepLApiKey.objects.get(id=key_id)
    except DeepLApiKey.DoesNotExist:
        return

    try:
        translator = deepl.Translator(deepl_key.api_key)
        usage = translator.get_usage()

        if (
            usage.character.limit is None
            or usage.character.count < usage.character.limit
        ):
            deepl_key.status = DeepLApiKey.Status.ACCEPTED
        else:
            deepl_key.status = DeepLApiKey.Status.REJECTED
    except deepl.exceptions.AuthorizationException:
        deepl_key.status = DeepLApiKey.Status.REJECTED
    except deepl.exceptions.QuotaExceededException:
        deepl_key.status = DeepLApiKey.Status.REJECTED
    except deepl.exceptions.DeepLException:
        deepl_key.status = DeepLApiKey.Status.REJECTED
    deepl_key.save()
