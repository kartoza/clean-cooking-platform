# Generated by Django 2.2.16 on 2021-11-25 08:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0046_auto_20211123_0702'),
    ]

    operations = [
        migrations.AddField(
            model_name='geography',
            name='household_layer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='household_layer', to='layers.Layer'),
        ),
    ]