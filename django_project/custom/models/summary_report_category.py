from django.db import models
from geonode.layers.models import Layer
from custom.models.preset import Preset

ANALYSIS_CHOICES = (
    ('ani', 'ANI'),
    ('ccp', 'CCP'),
    ('supply', 'Supply'),
    ('supply_demand', 'Supply and Demand'),
)


class SummaryReportCategory(models.Model):

    name = models.CharField(
        max_length=255,
        null=False,
        blank=False
    )

    preset = models.ForeignKey(
        Preset,
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )

    category = models.CharField(
        max_length=255,
        default='',
        blank=True,
        help_text='To be displayed in the table for the total value e.g. '
                  'Total Number of health facilities.'
    )

    show_percentage = models.BooleanField(
        default=False,
        help_text='Show percentage value rather than absolute value.'
    )

    analysis = models.CharField(
        choices=ANALYSIS_CHOICES,
        max_length=100,
        default='',
        blank=True,
    )

    vector_layer = models.ForeignKey(
        Layer,
        related_name='vector_layer',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text='Vector layer used to query the data. '
                  'Needed for CCP or Supply analysis.'
    )

    supply_layer = models.ForeignKey(
        Layer,
        related_name='supply_layer',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text='Raster layer used for ANI analysis calculation. '
                  'e.g. To calculate population in areas close to LPG '
                  'supply under poverty line, we need to include LPG '
                  'distance raster layer here.'
    )

    def __str__(self):
        return f'{self.name}-{self.preset.name}'

    class Meta:
        verbose_name_plural = 'Summary Report Categories'
        verbose_name = 'Summary Report Category'
