# Generated by Django 2.2.16 on 2021-05-17 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0018_auto_20210517_0226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasetfile',
            name='use_geonode_layer',
            field=models.BooleanField(default=True),
        ),
    ]
