from django.db import models


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
