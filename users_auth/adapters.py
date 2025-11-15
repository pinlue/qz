from typing import Any

from allauth.account.adapter import DefaultAccountAdapter

from qz.settings import EMAIL_VERIFICATION_URL
from .tasks import send_registration_email


class CustomAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix: str, email: str, context: dict[str, Any]):
        send_registration_email.delay("Register", f"{EMAIL_VERIFICATION_URL}?key={context['key']}", [email])
