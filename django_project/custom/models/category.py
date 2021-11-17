# coding=utf-8
"""Category model definition.
"""
from django.contrib.gis.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver

from custom.models.unit import Unit
from custom.utils.cache import delete_all_dataset_cache

LINEAR = 'linear'
INTERVALS = 'intervals'
KEY_DELTA = 'key-delta'
INCLUSION_BUFFER = 'inclusion-buffer'


class Category(models.Model):
    """Category model"""

    INDEX_SCALES = (
        (LINEAR, 'Linear'),
        (INTERVALS, 'Intervals'),
        (KEY_DELTA, 'Key Delta'),
        (INCLUSION_BUFFER, 'Inclusion Buffer')
    )

    geography = models.ForeignKey(
        'custom.Geography',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    name_long = models.TextField(
        verbose_name='Name',
        blank=True
    )

    unit_object = models.ForeignKey(
        Unit,
        verbose_name='Unit',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
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

    boundary_layer = models.BooleanField(
        default=False
    )

    weight = models.BooleanField(
        default=True
    )

    order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False
    )

    analysis = JSONField(
        null=True,
        blank=True,
        default= {
            "clamp": False,
            "index": "supply",
            "scale": "linear",
            "weight": 2,
            "indexes": [],
            "intervals": {}
        }
    )

    timeline = JSONField(
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

    sidebar_sub_menu_obj = models.ForeignKey(
        'custom.SubMenu',
        related_name='category_sidebar_sub_menu',
        verbose_name='Sidebar menu',
        help_text='[Main Menu] - Sub Menu',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )

    legend_range_steps = models.IntegerField(
        verbose_name='Range steps',
        null=True,
        blank=True,
        default=10
    )

    range_type = models.CharField(
        max_length=128,
        default='double',
        help_text='Range data type, e.g. double',
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

    # Index
    eap_use = models.BooleanField(
        default=False,
        verbose_name='Use Energy Access Potential',
        help_text=(
            'The Energy Access Potential Index identifies areas with higher '
            'energy demand and supply which are characterized with higher '
            'index values. It is an aggregated measure of all selected data '
            'sets under both Demand and Supply categories.'
        )
    )
    eap_scale = models.CharField(
        verbose_name='EAP Scale',
        max_length=50,
        choices=INDEX_SCALES,
        default='',
        blank=True,
    )
    eap_invert = models.BooleanField(
        verbose_name='Invert',
        default=False
    )

    demand_index = models.BooleanField(
        default=False,
        verbose_name='Use Demand',
        help_text=(
            'The Demand Index identifies areas with higher energy demand '
            'which are characterized with higher index values. '
            'It is an aggregated and weighted measure of all selected data '
            'sets under Demographics and Socio-economic activities.'
        )
    )
    demand_scale = models.CharField(
        verbose_name='Demand Scale',
        max_length=50,
        choices=INDEX_SCALES,
        default='',
        blank=True,
    )
    demand_invert = models.BooleanField(
        verbose_name='Invert',
        default=False
    )

    supply_index = models.BooleanField(
        default=False,
        verbose_name='Use Supply',
        help_text=(
            'The Supply Index identifies areas with higher energy '
            'supply which are characterized with higher index values. '
            'It is an aggregated and weighted measure of all selected data '
            'sets under Resource Availability and Infrastructure.'
        )
    )
    supply_scale = models.CharField(
        verbose_name='Supply Scale',
        max_length=50,
        choices=INDEX_SCALES,
        default='',
        blank=True,
    )
    supply_invert = models.BooleanField(
        verbose_name='Invert',
        default=False
    )

    ani_index = models.BooleanField(
        default=False,
        verbose_name='Use Assistance Need Index',
        help_text=(
            'The Assistance Need Index identifies areas where market '
            'assistance is needed the most which are characterized '
            'with higher index values. It is an aggregated and weighted '
            'measure of selected data sets under both Demand and Supply '
            'categories indicating high energy demand, low economic activity, '
            'and low access to infrastructure and resources.'
        )
    )
    ani_scale = models.CharField(
        verbose_name='ANI Scale',
        max_length=50,
        choices=INDEX_SCALES,
        default='',
        blank=True,
    )
    ani_invert = models.BooleanField(
        verbose_name='Invert',
        default=False
    )

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order']

    def __str__(self):
        return self.name_long


@receiver(post_delete, sender=Category)
def category_post_delete_handler(sender, **kwargs):
     delete_all_dataset_cache()


@receiver(post_save, sender=Category)
def category_post_save_handler(sender, **kwargs):
    delete_all_dataset_cache()
