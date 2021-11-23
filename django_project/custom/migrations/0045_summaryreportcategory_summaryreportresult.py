# Generated by Django 2.2.16 on 2021-11-23 02:34

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0044_auto_20211115_0842'),
    ]

    operations = [
        migrations.CreateModel(
            name='SummaryReportCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('preset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='custom.Preset')),
                ('vector_layer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='layers.Layer')),
            ],
            options={
                'verbose_name_plural': 'Summary Report Categories',
            },
        ),
        migrations.CreateModel(
            name='SummaryReportResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raster_file', models.FileField(blank=True, null=True, upload_to='summary_raster_file/')),
                ('category', models.CharField(blank=True, default='', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('result', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('summary_report_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='custom.SummaryReportCategory')),
            ],
            options={
                'verbose_name_plural': 'Summary Report Results',
            },
        ),
    ]