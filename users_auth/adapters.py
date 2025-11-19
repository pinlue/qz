from typing import Any

from allauth.account.adapter import DefaultAccountAdapter

from qz.settings import EMAIL_VERIFICATION_URL, PASSWORD_RESET_URL
from .tasks import send_registration_email


class CustomAccountAdapter(DefaultAccountAdapter):

    def send_mail(self, template_prefix, email, context):
        if "key" in context:
            url = f"{EMAIL_VERIFICATION_URL}?key={context['key']}"
            send_registration_email.delay("Verify email", url, [email])
            return None

        if "token" in context and "uid" in context:
            url = f"{PASSWORD_RESET_URL}?uid={context['uid']}&token={context['token']}"
            send_registration_email.delay("Reset password", url, [email])
            return None

        return super().send_mail(template_prefix, email, context)
