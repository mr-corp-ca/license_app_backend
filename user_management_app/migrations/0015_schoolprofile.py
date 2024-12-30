# Generated by Django 5.1.2 on 2025-01-01 14:36

import django.db.models.deletion
import django_extensions.db.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_management_app', '0018_alter_learnerselectedpackage_package'),
        ('user_management_app', '0014_schoolsetting_learner_alter_schoolsetting_instructor'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('institute_name', models.CharField(max_length=255)),
                ('instructor_name', models.CharField(max_length=255)),
                ('registration_file', models.FileField(upload_to='media/school/registration_file')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('license_category', models.ManyToManyField(blank=True, to='course_management_app.licensecategory')),
                ('services', models.ManyToManyField(blank=True, to='course_management_app.service')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
    ]