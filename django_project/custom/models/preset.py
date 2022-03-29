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

    population_ccp_text = models.CharField(
        blank=False,
        max_length=255,
        help_text='Description text in the report',
        default='Population within areas of high clean cooking '
                'potential index',
    )

    population_supply_text = models.CharField(
        blank=False,
        max_length=255,
        help_text='Description text in the report',
        default='Population within areas of high supply index'
    )

    population_ani_text = models.CharField(
        blank=False,
        max_length=255,
        help_text='Description text in the report',
        default='Population with medium to high '
                'Finance Needed Index'
    )

    class Meta:
        verbose_name_plural = 'Presets'
        ordering = ['order']

    def __str__(self):
        return self.name
