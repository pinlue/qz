from django.db import models
from django.conf import settings

from qz.settings import fernet


class ApiKeyBase(models.Model):
    _api_key = models.BinaryField()

    class Meta:
        abstract = True

    @property
    def api_key(self) -> str:
        return fernet.decrypt(self._api_key).decode()

    @api_key.setter
    def api_key(self, raw_key: str):
        self._api_key = fernet.encrypt(raw_key.encode())


class DeepLApiKey(ApiKeyBase):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")

    def __str__(self):
        return f"DeepL key for {self.user} [{self.status}]"
