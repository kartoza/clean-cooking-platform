# coding=utf-8
"""Geography model definition.
"""
import requests
import re
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from django.contrib.postgres.fields import JSONField
from geonode.layers.models import Layer


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
        verbose_name='ISO 3 Letter Country Code',
        help_text='Three-letter country code'
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

    vector_boundary_layer = models.ForeignKey(
        Layer,
        null=True,
        blank=True,
        related_name='vector_boundary_layer',
        on_delete=models.SET_NULL
    )

    raster_mask_layer = models.ForeignKey(
        Layer,
        null=True,
        blank=True,
        related_name='raster_mask_layer',
        on_delete=models.SET_NULL
    )

    household_layer = models.ForeignKey(
        Layer,
        null=True,
        blank=True,
        related_name='household_layer',
        on_delete=models.SET_NULL
    )

    household_layer_field = models.CharField(
        max_length=255,
        default='',
        blank=True,
        help_text='Field to get value from household layer'
    )

    urban_layer = models.ForeignKey(
        Layer,
        null=True,
        blank=True,
        related_name='urban_layer',
        on_delete=models.SET_NULL
    )

    cooking_percentage_layer = models.ForeignKey(
        Layer,
        null=True,
        blank=True,
        related_name='cooking_percentage_layer',
        on_delete=models.SET_NULL
    )

    cooking_percentage_layer_field = models.CharField(
        max_length=255,
        default='',
        blank=True,
        help_text='Field to get value from cooking percentage layer'
    )

    configuration = JSONField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='geography_created_by'
    )

    updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='geography_updated_by'
    )

    boundary_dimension_x = models.FloatField(
        default=100,
        help_text='Raster resolution (x)'
    )
    boundary_dimension_y = models.FloatField(
        default=100,
        help_text='Raster resolution (y)'
    )

    province_selector = models.TextField(
        max_length=255,
        blank=True,
        default=''
    )

    district_selector = models.TextField(
        max_length=255,
        blank=True,
        default=''
    )

    municipal_selector = models.TextField(
        max_length=255,
        blank=True,
        default=''
    )

    class Meta:
        verbose_name_plural = 'Geographies'

    def __str__(self):
        return self.name


@receiver(post_save, sender=Geography)
def post_save_geography(sender, instance, **kwargs):
    if not instance.raster_mask_layer:
        return

    if (
            instance.raster_mask_layer
    ):
        post_save.disconnect(post_save_geography, sender=sender)
        geoserver = settings.GEOSERVER_LOCATION
        url = (
            f'{geoserver}wcs?service=WCS&version=2.0.1&request='
            f'describecoverage&'
            f'coverageid={instance.raster_mask_layer.typename}'
        )
        r = requests.get(url = url)

        data = r.text
        grid_envelope = (
            re.findall('<gml:high>(.*?)</gml:high>', data, re.DOTALL)
        )
        if len(grid_envelope) > 0:
            x, y = grid_envelope[0].split(' ')
            instance.boundary_dimension_x = int(x)
            instance.boundary_dimension_y = int(y)
            instance.save()
        post_save.connect(post_save_geography, sender=sender)
