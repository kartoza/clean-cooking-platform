# Generated by Django 2.2.16 on 2021-05-24 04:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0024_auto_20210524_0342'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='sidebar_main_menu_obj',
        ),
        migrations.AlterField(
            model_name='category',
            name='sidebar_sub_menu_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='category_sidebar_sub_menu', to='custom.SubMenu', verbose_name='Sidebar sub menu'),
        ),
    ]
