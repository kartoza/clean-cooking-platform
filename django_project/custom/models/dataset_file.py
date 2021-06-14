# coding=utf-8
"""Datasets files model definition.
"""
import re
import requests
from django.contrib.gis.db import models
from django.conf import settings
from django.dispatch import receiver
from django.contrib.postgres.fields import JSONField
from geonode.layers.models import Layer

CSV = 'csv'
VECTORS = 'vectors'
RASTER = 'raster'

class DatasetFile(models.Model):
    """Datasets files model"""

    FUNC_CHOICES = (
        (CSV, 'CSV'),
        (VECTORS, 'Vectors'),
        (RASTER, 'Raster')
    )

    category = models.ForeignKey(
        'custom.Category',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    label = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        default=''
    )

    use_geonode_layer = models.BooleanField(
        default=True
    )

    endpoint = models.FileField(
        upload_to='datasets/',
        null=True,
        blank=True
    )

    geonode_layer = models.ForeignKey(
        Layer,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    func = models.CharField(
        max_length=50,
        choices=FUNC_CHOICES,
        default='',
        blank=True,
        verbose_name='Dataset File Type'
    )

    configuration = JSONField(
        null=True,
        blank=True
    )

    comment = models.TextField(
        default='',
        blank=True
    )

    active = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='dataset_file_created_by'
    )

    updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='dataset_file_updated_by'
    )

    def __str__(self):
        return f'{self.label if self.label else "-"} ({self.func.capitalize()})'

    class Meta:
        verbose_name_plural = 'Dataset Files'


@receiver(models.signals.post_save, sender=DatasetFile)
def post_save_dataset_file(sender, instance, **kwargs):
    if not instance.category:
        return

    if (
            instance.geonode_layer and
            instance.category.boundary_layer and
            instance.func == RASTER
    ):
        geoserver = settings.GEOSERVER_LOCATION
        url = (
            f'{geoserver}wcs?service=WCS&version=2.0.1&request='
            f'describecoverage&coverageid={instance.geonode_layer.typename}'
        )
        r = requests.get(url = url)

        data = r.text
        grid_envelope = (
            re.findall('<gml:high>(.*?)</gml:high>', data, re.DOTALL)
        )
        if len(grid_envelope) > 0:
            x, y = grid_envelope[0].split(' ')
            geography = instance.category.geography
            geography.boundary_dimension_x = int(x)
            geography.boundary_dimension_y = int(y)
            geography.save()
