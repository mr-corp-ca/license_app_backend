# Generated by Django 4.2.17 on 2025-02-11 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_management_app', '0009_course_road_test_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='selectedsubscriptionpackagepaln',
            name='Stripe_secret_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='selectedsubscriptionpackagepaln',
            name='package_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=255),
        ),
    ]
