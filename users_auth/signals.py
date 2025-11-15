from __future__ import annotations
from typing import TYPE_CHECKING

from django.db import transaction
from django.dispatch import receiver
from allauth.account.signals import email_confirmed

from common.models import ScheduledTask
from allauth.account.models import EmailAddress

if TYPE_CHECKING:
    from rest_framework.request import Request
    from typing import Any


@receiver(email_confirmed)
def handle_email_confirmed(request: Request, email_address: EmailAddress, **kwargs: Any) -> None:
    user = email_address.user

    with transaction.atomic():
        email_address.primary = True
        email_address.verified = True
        email_address.save(update_fields=["primary", "verified"])

        EmailAddress.objects.filter(user=user).exclude(pk=email_address.pk).delete()

        try:
            ScheduledTask.objects.get(
                name="users_auth.tasks.delete_unverified_email",
                kwargs__user_id=user.id,
                kwargs__email=email_address.email,
            ).delete()
        except ScheduledTask.DoesNotExist:
            pass
