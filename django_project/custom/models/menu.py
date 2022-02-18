from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from custom.utils.cache import delete_all_dataset_cache


class Menu(models.Model):
    order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False
    )

    name = models.CharField(
        max_length=128,
        null=False,
        blank=False
    )

    class Meta:
        abstract = True
        ordering = ['order']

    def __str__(self):
        return self.name


class MainMenu(Menu):
    geography = models.ForeignKey(
        'custom.Geography',
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = 'Main menu'
        ordering = ['order']


class SubMenu(Menu):
    main_menu = models.ForeignKey(
        'custom.MainMenu',
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'[{self.main_menu.name}] - {self.name}'

    class Meta:
        verbose_name_plural = 'Sub menu'
        ordering = ['order']


@receiver(post_save, sender=MainMenu)
@receiver(post_save, sender=SubMenu)
def menu_post_save_handler(sender, **kwargs):
     delete_all_dataset_cache()
