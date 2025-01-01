# Generated by Django 4.2.17 on 2025-01-01 20:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course_management_app', '0019_merge_20250102_0049'),
    ]

    operations = [
        migrations.AddField(
            model_name='courserating',
            name='courese_status',
            field=models.CharField(choices=[('on-going', 'On Going'), ('completed', 'Completed'), ('rejected', 'Rejected')], default='on-going', max_length=255),
        ),
        migrations.AddField(
            model_name='courserating',
            name='learner_selected_package',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='courserating',
            name='package',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='course_management_app.package'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='courserating',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='About'),
        ),
        migrations.AlterField(
            model_name='course',
            name='lesson',
            field=models.ManyToManyField(default=None, related_name='course_lessons', to='course_management_app.lesson'),
        ),
        migrations.AlterField(
            model_name='course',
            name='price',
            field=models.FloatField(default=0.0, verbose_name='price per lesson'),
        ),
    ]
