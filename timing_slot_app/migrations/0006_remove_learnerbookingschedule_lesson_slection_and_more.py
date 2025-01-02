# Generated by Django 5.1.2 on 2025-01-02 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timing_slot_app', '0005_alter_learnerbookingschedule_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='learnerbookingschedule',
            name='lesson_slection',
        ),
        migrations.AddField(
            model_name='learnerbookingschedule',
            name='hire_car',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='learnerbookingschedule',
            name='special_lesson',
            field=models.BooleanField(default=False),
        ),
    ]