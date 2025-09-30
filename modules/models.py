from django.db import models
from rest_framework.exceptions import ValidationError

from abstracts.models import Tags, Visibles
from users.models import User


class Module(Tags, Visibles, models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='modules')
    topic = models.ForeignKey('topics.Topic', on_delete=models.CASCADE, related_name='modules')
    lang_from = models.ForeignKey('languages.Language', on_delete=models.CASCADE, related_name='modules_from_lang')
    lang_to = models.ForeignKey('languages.Language', on_delete=models.CASCADE, related_name='modules_to_lang')

    folders = models.ManyToManyField('folders.Folder', related_name='modules')

    class Meta:
        ordering = ['name']

    def clean(self):
        if self.lang_from == self.lang_to:
            raise ValidationError("Source and target languages must be different.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
