# Generated by Django 2.2.16 on 2021-04-05 11:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0005_auto_20210330_0756'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasetfile',
            name='geonode_layer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='layers.Layer'),
        ),
        migrations.AddField(
            model_name='datasetfile',
            name='use_geonode_layer',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='datasetfile',
            name='endpoint',
            field=models.FileField(blank=True, null=True, upload_to='datasets/'),
        ),
    ]