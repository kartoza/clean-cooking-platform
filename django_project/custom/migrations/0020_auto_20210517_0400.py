# Generated by Django 2.2.16 on 2021-05-17 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0019_auto_20210517_0307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geography',
            name='adm',
            field=models.IntegerField(default=0),
        ),
    ]
