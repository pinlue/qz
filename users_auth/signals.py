from django.dispatch import receiver
from allauth.account.signals import email_confirmed

from common.models import ScheduledTask
from allauth.account.models import EmailAddress


@receiver(email_confirmed)
def handle_email_confirmed(request, email_address, **kwargs):
    user = email_address.user
    email_address.primary = True
    email_address.save()

    EmailAddress.objects.filter(user=user).exclude(pk=email_address.pk).delete()

    try:
        ScheduledTask.objects.get(
            name='users_auth.tasks.delete_unverified_email',
            kwargs__user_id=user.id,
            kwargs__email=email_address.email
        ).delete()
    except ScheduledTask.DoesNotExist:
        pass