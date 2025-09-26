from django.core import validators
from django.db import models


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(
        max_length=3,
        unique=True,
        validators=[
            validators.RegexValidator(
                regex=r'^[A-Z]{2,3}$',
                message='Code must be 2 or 3 uppercase English letters.'
            )
        ]
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
