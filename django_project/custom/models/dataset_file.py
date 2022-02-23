# coding=utf-8
"""Datasets files model definition.
"""
import re

import os
import shutil

import requests
from django.contrib.gis.db import models
from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import JSONField
from geonode.layers.models import Layer, Style

from custom.utils.cache import delete_vector_point_cache

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


def remove_dataset_cache(dataset: DatasetFile, layer: Layer):
    from custom.models import ClippedLayer

    cache.delete('style_dataset_{}'.format(dataset.id))

    # Remove clipped layers if exist
    clipped_layers = ClippedLayer.objects.filter(layer=layer)
    if clipped_layers.exists():
        clipped_layers.delete()

    # Remove cached style
    dataset_style_folder = os.path.join(
        settings.MEDIA_ROOT, 'styles', str(dataset.id))

    if os.path.exists(dataset_style_folder):
        shutil.rmtree(dataset_style_folder)


@receiver(post_save, sender=Layer)
@receiver(post_save, sender=Style)
def layer_post_save(sender, instance, created, **kwargs):
    if created:
        return
    if isinstance(instance, Layer):
        delete_vector_point_cache(instance.id)
    if isinstance(instance, Style):
        instance = instance.layer_default_style.first()
    dataset = None
    try:
        dataset = instance.datasetfile_set.first()
    except:  # noqa
        return
    finally:
        if not dataset:
            return
    remove_dataset_cache(dataset, instance)
