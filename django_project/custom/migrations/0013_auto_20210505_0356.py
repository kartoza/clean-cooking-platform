# Generated by Django 2.2.16 on 2021-05-05 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0012_auto_20210427_0918'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='legend_range_steps',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='sidebar_main_menu',
            field=models.CharField(default='-', max_length=125),
        ),
        migrations.AddField(
            model_name='category',
            name='sidebar_sub_menu',
            field=models.CharField(default='-', max_length=125),
        ),
    ]