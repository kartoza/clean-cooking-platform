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
        default='',
        max_length=512
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

    ccp_use = models.BooleanField(
        default=False,
        verbose_name='Use Clean Cooking Potential Index'
    )

    supply_index = models.BooleanField(
        default=False,
        verbose_name='Use Supply Index'
    )

    ani_index = models.BooleanField(
        default=False,
        verbose_name='Use Assistance Need Index'
    )

    class Meta:
        verbose_name_plural = 'Presets'
        ordering = ['order']

    def __str__(self):
        return self.name
