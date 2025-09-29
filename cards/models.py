from django.db import models


class Card(models.Model):
    original = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)

    module = models.ForeignKey('modules.Module', on_delete=models.CASCADE, related_name='cards')

    class Meta:
        ordering = ['original']
        unique_together = ('original', 'translation', 'module')

    def __str__(self):
        return f"{self.original} - {self.translation}"
