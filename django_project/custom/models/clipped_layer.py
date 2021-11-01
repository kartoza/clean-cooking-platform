# coding=utf-8
"""Clipped layer model definition.
"""
import os
from django.conf import settings
from django.contrib.gis.db import models
from django.core.files.storage import FileSystemStorage

from geonode.layers.models import Layer

VECTOR = 'vector'
RASTER = 'raster'


class ClippedFileStorage(FileSystemStorage):

    def get_available_name(self, name):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

cfs = ClippedFileStorage()


class ClippedLayer(models.Model):
    """Clipped layer model"""

    LAYER_TYPE_CHOICES = (
        (VECTOR, 'vector'),
        (RASTER, 'raster')
    )

    layer = models.ForeignKey(
        Layer,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    clipped_file = models.FileField(
        upload_to='clipped_layers/',
        null=True,
        blank=True,
        max_length=300,
        storage=cfs
    )

    created_date = models.DateTimeField(
        auto_now_add=True
    )

    boundary_uuid = models.CharField(
        max_length=255,
        default='',
        blank=True
    )

    layer_type = models.CharField(
        choices=LAYER_TYPE_CHOICES,
        max_length=100,
        default='',
        blank=True,
    )

    process_state = models.CharField(
        max_length=200,
        default='',
        blank=True
    )
