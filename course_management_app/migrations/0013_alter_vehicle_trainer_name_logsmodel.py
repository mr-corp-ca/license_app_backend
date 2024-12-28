# Generated by Django 5.1.2 on 2024-12-28 18:39

import django.db.models.deletion
import django_extensions.db.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_management_app', '0012_vehicle_instructor_alter_vehicle_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='trainer_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Trainer Name'),
        ),
        migrations.CreateModel(
            name='LogsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('json_data', models.TextField()),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
    ]