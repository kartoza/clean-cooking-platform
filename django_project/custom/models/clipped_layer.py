# coding=utf-8
"""Clipped layer model definition.
"""
import os
import shutil

from django.conf import settings
from django.contrib.gis.db import models
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_save
from django.dispatch import receiver

from geonode.layers.models import Layer

VECTOR = 'vector'
RASTER = 'raster'

SUCCESS = 'success'
PENDING = 'pending'
FAILED = 'failed'


class ClippedFileStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
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

    STATE_CHOICES = (
        (PENDING, 'Pending'),
        (SUCCESS, 'Success'),
        (FAILED, 'Failed')
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
        blank=True,
        help_text='Process ID'
    )

    state = models.CharField(
        max_length=50,
        default='',
        blank=True,
        choices=STATE_CHOICES,
    )

    @property
    def successful(self):
        return self.state == SUCCESS and self.clipped_file

    @property
    def pending(self):
        return self.state == PENDING and self.process_state

    @property
    def failed(self):
        return self.state == FAILED


@receiver(post_save, sender=ClippedLayer)
def clipped_layer_post_save(sender, instance: ClippedLayer, created, **kwargs):
    from custom.utils.cache import delete_all_dataset_cache
    if instance.successful:
        delete_all_dataset_cache()
    output_folder = os.path.join(
        settings.MEDIA_ROOT,
        'clipped_temp',
        f'{str(instance.layer)}:{instance.boundary_uuid}'
    )
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

