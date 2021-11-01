from django.db import models
from custom.models.preset import Preset

class UseCase(models.Model):

    name = models.CharField(
        max_length=255,
        blank=False
    )

    description = models.TextField(
        blank=False
    )

    order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False
    )

    presets = models.ManyToManyField(
        Preset,
        null=False
    )

    class Meta:
        verbose_name_plural = 'Use Cases'
        ordering = ['order']

    def __str__(self):
        return self.name
    