# Generated by Django 2.2.16 on 2021-11-01 04:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0038_usecase'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClippedLayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clipped_file', models.FileField(upload_to='clipped_layers/')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('boundary_uuid', models.CharField(blank=True, default='', max_length=255)),
                ('layer_type', models.CharField(blank=True, choices=[('vector', 'vector'), ('raster', 'raster')], default='', max_length=100)),
                ('process_state', models.CharField(blank=True, default='', max_length=200)),
                ('layer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='layers.Layer')),
            ],
        ),
    ]
