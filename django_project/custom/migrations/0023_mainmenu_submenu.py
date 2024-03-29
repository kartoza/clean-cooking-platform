# Generated by Django 2.2.16 on 2021-05-24 03:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0022_auto_20210524_0300'),
    ]

    operations = [
        migrations.CreateModel(
            name='MainMenu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(max_length=128)),
                ('geography', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='custom.Geography')),
            ],
            options={
                'ordering': ['order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubMenu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(max_length=128)),
                ('main_menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='custom.MainMenu')),
            ],
            options={
                'ordering': ['order'],
                'abstract': False,
            },
        ),
    ]
