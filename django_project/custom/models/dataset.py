# coding=utf-8
"""Datasets model definition.
"""
from django.contrib.gis.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField


class Dataset(models.Model):
    """Datasets model"""

    category = models.ForeignKey(
        'custom.Category',
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )

    geography = models.ForeignKey(
        'custom.Geography',
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=100,
        default="",
        blank=True
    )

    name_long = models.TextField(
        blank=True
    )

    unit = models.TextField(
        blank=True
    )

    pack = models.CharField(
        default="all",
        max_length=50,
        blank=True
    )

    circle = models.CharField(
        default="public",
        max_length=50,
        blank=True
    )

    online = models.BooleanField(
        default=True
    )

    presets = JSONField(
        null=True,
        blank=True
    )

    configuration = JSONField(
        null=True,
        blank=True
    )

    category_overrides = JSONField(
        null=True,
        blank=True
    )

    metadata = JSONField(
        default={
            'description': '',
            'suggested_citation': '',
            'cautions': '',
            'spatial_resolution': '',
            'license': '',
            'sources': '',
            'content_date': '',
            'download_original_url': '',
            'learn_more_url': ''
        },
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='dataset_created_by'
    )

    updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='dataset_updated_by'
    )

    class Meta:
        verbose_name_plural = 'Datasets'

    def __str__(self):
        return self.name
