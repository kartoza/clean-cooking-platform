from django.db import models
from preferences.models import Preferences


class CCAPreferences(Preferences):
    boundary_dimension_x = models.FloatField(
        default=100
    )
    boundary_dimension_y = models.FloatField(
        default=100
    )

    class Meta:
        verbose_name_plural = 'CCA Preferences'
