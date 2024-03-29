# Generated by Django 2.2.16 on 2021-06-14 07:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0033_auto_20210614_0709'),
    ]

    operations = [
        migrations.AddField(
            model_name='geography',
            name='raster_mask_layer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='raster_mask_layer', to='layers.Layer'),
        ),
        migrations.AddField(
            model_name='geography',
            name='vector_boundary_layer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vector_boundary_layer', to='layers.Layer'),
        ),
    ]
