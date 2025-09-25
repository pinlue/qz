from django.contrib.auth.models import AbstractUser
from django.db import models

from users.utils import user_avatar_path


class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to=user_avatar_path, blank=True, null=True)

    def __str__(self):
        return self.username

