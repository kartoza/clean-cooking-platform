from django.db import models
from geonode.layers.models import Layer
from custom.models.preset import Preset

ANALYSIS_CHOICES = (
    ('ANI', 'ani'),
    ('CCP', 'ccp'),
    ('Supply', 'supply'),
)


class SummaryReportCategory(models.Model):

    name = models.CharField(
        max_length=255,
        null=False,
        blank=False
    )

    vector_layer = models.ForeignKey(
        Layer,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    supply_layer = models.ForeignKey(
        Layer,
        related_name='supply_layer',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    preset = models.ForeignKey(
        Preset,
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )

    analysis = models.CharField(
        choices=ANALYSIS_CHOICES,
        max_length=100,
        default='',
        blank=True,
    )

    def __str__(self):
        return f'{self.name}-{self.preset.name}'

    class Meta:
        verbose_name_plural = 'Summary Calculation Categories'
        verbose_name = 'Summary Calculation Category'
