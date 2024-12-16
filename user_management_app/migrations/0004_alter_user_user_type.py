# Generated by Django 5.1.2 on 2024-12-09 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management_app', '0003_user_is_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('admin', 'Owner Admin'), ('learner', 'Learner'), ('instructor', 'Instructor')], max_length=255),
        ),
    ]