# Generated by Django 4.2.17 on 2024-12-10 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils_app', '0002_radius_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='radius',
            name='main_latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='radius',
            name='main_location_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Main Radius'),
        ),
        migrations.AlterField(
            model_name='radius',
            name='main_longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
    ]
