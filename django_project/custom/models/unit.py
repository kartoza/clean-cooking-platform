from django.db import models


class Unit(models.Model):

    name = models.CharField(
        max_length=128,
        null=False,
        blank=False
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name
