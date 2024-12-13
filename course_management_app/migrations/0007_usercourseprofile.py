# Generated by Django 4.2.17 on 2024-12-12 13:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course_management_app', '0006_vehicle_booking_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCourseProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('courses', models.ManyToManyField(related_name='user_profiles', to='course_management_app.course')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='course_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
    ]
