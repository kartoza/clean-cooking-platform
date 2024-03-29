# Generated by Django 2.2.16 on 2021-05-17 02:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0017_auto_20210511_0821'),
    ]

    operations = [
        migrations.AddField(
            model_name='geography',
            name='icon',
            field=models.FileField(blank=True, null=True, upload_to='geography_icons/'),
        ),
        migrations.AlterField(
            model_name='geography',
            name='cca3',
            field=models.CharField(help_text='Three-letter country codes', max_length=3, verbose_name='CCA3'),
        ),
    ]
