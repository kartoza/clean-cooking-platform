# coding=utf-8
"""Category model definition.
"""
from django.contrib.gis.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField


class Category(models.Model):
    """Category model"""

    geography = models.ForeignKey(
        'custom.Geography',
        null=True,
        blank=True,
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

    unit = models.CharField(
        max_length=32,
        blank=True
    )

    domain = JSONField(
        null=True,
        blank=True
    )

    domain_init = JSONField(
        null=True,
        blank=True
    )

    colorstops = JSONField(
        null=True,
        blank=True
    )

    raster = JSONField(
        null=True,
        blank=True
    )

    vectors = JSONField(
        null=True,
        blank=True
    )

    csv = JSONField(
        null=True,
        blank=True
    )

    analysis = JSONField(
        null=True,
        blank=True,
        default= {
            "clamp": False,
            "index": "supply",
            "scale": "linear",
            "weight": 2,
            "indexes": [
                {
                    "index": "supply",
                    "scale": "linear",
                    "invert": True
                },
                {
                    "index": "eai",
                    "scale": "linear",
                    "invert": True
                },
                {
                    "index": "ani",
                    "scale": "linear",
                    "invert": True
                }
            ],
            "intervals": {}
        }
    )

    timeline = JSONField(
        null=True,
        blank=True
    )

    configuration = JSONField(
        null=True,
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

    sidebar_main_menu = models.CharField(
        default='-',
        blank=False,
        null=False,
        max_length=125
    )

    sidebar_sub_menu = models.CharField(
        default='-',
        blank=False,
        null=False,
        max_length=125
    )

    legend_range_steps = models.IntegerField(
        null=True,
        blank=True
    )

    controls = JSONField(
        default={
            'range': '',
            'range_steps': '',
            'range_label': '',
            'path': [],
            'weight': False
        },
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
        related_name='category_created_by'
    )

    updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='category_updated_by'
    )

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name_long
