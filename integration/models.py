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
    def api_key(self, raw_key: str) -> None:
        self._api_key = fernet.encrypt(raw_key.encode())


class DeepLApiKey(ApiKeyBase):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )

    def __str__(self) -> str:
        return f"DeepL key for {self.user} [{self.status}]"
