# Generated by Django 4.2.17 on 2025-01-09 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_management_app', '0006_instructorlesson'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
