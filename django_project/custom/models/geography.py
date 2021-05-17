# coding=utf-8
"""Geography model definition.
"""
from django.contrib.gis.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField


class Geography(models.Model):
    """Geography model"""

    name = models.CharField(
        max_length=100,
        blank=False
    )

    parent = models.ForeignKey(
        verbose_name='Parent',
        to='self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    adm = models.IntegerField(
        default=0
    )

    cca3 = models.CharField(
        max_length=3,
        blank=False,
        verbose_name='CCA3',
        help_text='Three-letter country codes'
    )

    circle = models.CharField(
        max_length=50,
        default="",
        blank=True
    )

    pack = models.CharField(
        max_length=50,
        default="",
        blank=True
    )

    online = models.BooleanField(
        default=True
    )

    icon = models.FileField(
        null=True,
        blank=True,
        upload_to='geography_icons/'
    )

    boundary_file = models.FileField(
        null=True,
        blank=True,
        upload_to="boundary/"
    )

    configuration = JSONField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name='geography_created_by'
    )

    updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name='geography_updated_by'
    )

    class Meta:
        verbose_name_plural = 'Geographies'

    def __str__(self):
        return self.name
