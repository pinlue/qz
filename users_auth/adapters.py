from allauth.account.adapter import DefaultAccountAdapter

from .tasks import send_registration_email


class CustomAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        msg = self.render_mail(template_prefix, email, context)
        send_registration_email.delay(msg.subject, msg.body, [email])