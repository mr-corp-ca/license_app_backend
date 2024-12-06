# Generated by Django 5.1.2 on 2024-12-02 09:33

import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('price', models.FloatField(default=0.0)),
                ('lesson_numbers', models.PositiveIntegerField()),
                ('refund_policy', models.TextField(blank=True, null=True)),
                ('course_cover_image', models.ImageField(upload_to='course_images/')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LicenseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, verbose_name='Vehicle Name')),
                ('trainer_name', models.CharField(max_length=255, verbose_name='Trainer Name')),
                ('vehicle_registration_no', models.CharField(max_length=100, unique=True, verbose_name='Registration Number')),
                ('license_number', models.CharField(max_length=100, unique=True, verbose_name='License Number')),
                ('vehicle_model', models.CharField(max_length=100, verbose_name='Vehicle Model')),
                ('image', models.ImageField(blank=True, null=True, upload_to='vehicle_images/', verbose_name='Vehicle Image')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
    ]
