# Generated by Django 4.2.17 on 2025-01-10 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timing_slot_app', '0008_learnerbookingschedule_is_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='learnerbookingschedule',
            name='lesson_name',
            field=models.TextField(blank=True, default='Lesson', null=True),
        ),
    ]
