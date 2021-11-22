from django.db import models
from django.contrib.postgres.fields import JSONField
from geonode.layers.models import Layer
from custom.models.preset import Preset


class ReportSummary(models.Model):

    name = models.CharField(
        max_length=255,
        null=False,
        blank=False
    )

    vector_layer = models.ForeignKey(
        Layer,
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )

    raster_file = models.FileField(
        null=True,
        blank=True,
        upload_to="summary_raster_file/"
    )

    preset = models.ForeignKey(
        Preset,
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )

    category = models.CharField(
        max_length=100,
        blank=True,
        default=''
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    result = JSONField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Report summaries'
        