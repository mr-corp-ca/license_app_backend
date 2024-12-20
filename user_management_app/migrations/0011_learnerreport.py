# Generated by Django 4.2.17 on 2024-12-20 12:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('user_management_app', '0010_schoolsetting'),
    ]

    operations = [
        migrations.CreateModel(
            name='LearnerReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('reason', models.CharField(blank=True, choices=[('waiting-too-long', 'Waiting too long on a location'), ('misbehaving', 'Misbehaving'), ('abusing', 'Abusing'), ('others', 'Others')], max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learnerreport_instructor', to=settings.AUTH_USER_MODEL)),
                ('learner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learnerreport_learner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
    ]
