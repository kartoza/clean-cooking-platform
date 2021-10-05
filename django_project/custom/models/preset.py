from django.db import models


class Preset(models.Model):

    name = models.CharField(
        null=False,
        blank=False,
        max_length=255
    )

    description = models.TextField(
        default=''
    )

    permalink = models.URLField(
        verbose_name='Permalink Snippet',
        default=''
    )

    image = models.ImageField(
        upload_to='presets',
        null=True,
        blank=True
    )

    order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False
    )

    class Meta:
        verbose_name_plural = 'Presets'
        ordering = ['order']
