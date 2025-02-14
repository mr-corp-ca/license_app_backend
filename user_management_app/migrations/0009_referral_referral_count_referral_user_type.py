# Generated by Django 4.2.17 on 2025-02-01 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management_app', '0008_referral'),
    ]

    operations = [
        migrations.AddField(
            model_name='referral',
            name='referral_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='referral',
            name='user_type',
            field=models.CharField(choices=[('school', 'School'), ('learner', 'Learner')], default='learner', max_length=10),
        ),
    ]
