# Generated by Django 4.2.17 on 2025-02-06 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_management_app', '0008_alter_userselectedcourses_courses'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='road_test_price',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
