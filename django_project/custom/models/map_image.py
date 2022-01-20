
from django.db import models
from geonode.layers.models import Layer


class MapImage(models.Model):
    """Auxiliary model for storing map images.
    """

    preset = models.ForeignKey(
        'custom.Preset',
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )

    image = models.FileField(
        null=False,
        blank=False,
        upload_to='map_images/'
    )

    geonode_layer = models.ForeignKey(
        Layer,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    boundary_uuid = models.CharField(
        max_length=255,
        default='',
        blank=True
    )

    created_at =  models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
       if self.geonode_layer:
           return self.geonode_layer.name
       return self.image.path
