from datetime import timedelta

from allauth.account.models import EmailConfirmation, EmailAddress
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from common.models import ScheduledTask


def schedule_email_deletion(user_id, email, delay_days=3):
    scheduled_time = timezone.now() + timedelta(days=delay_days)
    task, created = ScheduledTask.objects.update_or_create(
        name='users_auth.tasks.delete_unverified_email',
        kwargs={'user_id': user_id, 'email': email},
        defaults={'scheduled_time': scheduled_time, 'status': 'pending'}
    )
    return task


@shared_task
def send_registration_email(subject, message, recipient_list):
    send_mail(subject, message, 'from@example.com', recipient_list)


@shared_task
def delete_unverified_email(user_id, email):
    try:
        email_obj = EmailAddress.objects.get(user_id=user_id, email=email, verified=False)
        email_obj.delete()
    except EmailAddress.DoesNotExist:
        raise ValueError(f"EmailAddress with user_id={user_id} and email={email} does not exist or already verified.")


@shared_task
def send_verification_email(user_id, email):
    email_obj = EmailAddress.objects.get(user_id=user_id, email=email)
    confirmation = EmailConfirmation.create(email_obj)
    confirmation.sent = timezone.now()
    confirmation.save()

    send_mail(
        subject="Email verification",
        message=f"Your verification code: {settings.EMAIL_VERIFICATION_URL}/?key={confirmation.key}",
        from_email="from@example.com",
        recipient_list=[email_obj.email],
    )