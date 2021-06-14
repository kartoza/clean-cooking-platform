from django.db import models
from preferences.models import Preferences


class CCAPreferences(Preferences):
    class Meta:
        verbose_name_plural = 'CCA Preferences'
