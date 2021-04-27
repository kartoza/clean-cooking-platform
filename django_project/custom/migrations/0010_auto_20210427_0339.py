# Generated by Django 2.2.16 on 2021-04-27 03:39

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0009_delete_dataset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='analysis',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={'clamp': False, 'index': 'supply', 'indexes': [{'index': 'supply', 'invert': True, 'scale': 'linear'}, {'index': 'eai', 'invert': True, 'scale': 'linear'}, {'index': 'ani', 'invert': True, 'scale': 'linear'}], 'intervals': {}, 'scale': 'linear', 'weight': 2}, null=True),
        ),
    ]
