# Generated by Django 5.1.2 on 2025-01-02 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timing_slot_app', '0003_monthlyschedule_lesson_duration_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='monthlyschedule',
            name='shift_timing',
            field=models.PositiveIntegerField(blank=True, default=0, help_text='Shift timing in hours', null=True),
        ),
    ]
