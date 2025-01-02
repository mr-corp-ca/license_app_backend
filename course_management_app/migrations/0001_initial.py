# Generated by Django 5.1.2 on 2025-01-02 16:48

import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('about', models.TextField(blank=True, null=True)),
                ('signature', models.CharField(max_length=255)),
                ('logo', models.ImageField(upload_to='logos/')),
                ('image', models.ImageField(blank=True, null=True, upload_to='certificate/')),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True, verbose_name='About')),
                ('price', models.FloatField(default=0.0, verbose_name='price per lesson')),
                ('lesson_numbers', models.PositiveIntegerField()),
                ('refund_policy', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DiscountOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('offer_type', models.CharField(choices=[('flat_discount', 'Flat Discount'), ('percentage_discount', 'Percentage Discount'), ('custom_offer', 'Custom Offer')], max_length=255, verbose_name='Package Name')),
                ('name', models.CharField(max_length=255, verbose_name='Package Name')),
                ('audience', models.CharField(choices=[('new_user', 'New User'), ('old_user', 'Old User'), ('loyal_user', 'Loyal User'), ('referral_user', 'Referral User'), ('all_users', 'All Users')], max_length=255, verbose_name='Package Name')),
                ('discount', models.PositiveIntegerField(default=0, verbose_name='Discount & offers(%)')),
                ('start_date', models.DateField(verbose_name='Start Date')),
                ('end_date', models.DateField(verbose_name='End Date')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LearnerSelectedPackage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('attended_lesson', models.PositiveIntegerField(default=0)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('courese_status', models.CharField(choices=[('on-going', 'On Going'), ('completed', 'Completed'), ('rejected', 'Rejected')], default='on-going', max_length=255)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('image', models.ImageField(upload_to='Lesson/images')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LicenseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, verbose_name='Package Name')),
                ('price', models.FloatField(default=0.0, verbose_name='Package Price')),
                ('total_course_hour', models.CharField(max_length=255, verbose_name='Total Course Hour')),
                ('lesson_numbers', models.PositiveIntegerField(verbose_name='Lesson Number')),
                ('free_pickup', models.FloatField(default=0.0, verbose_name='Free Pickup')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SchoolRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('rating', models.PositiveIntegerField(default=0)),
                ('learner_selected_package', models.PositiveIntegerField(default=0)),
                ('start_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SelectedSubscriptionPackagePaln',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('expired', models.DateTimeField(verbose_name='Package Expired')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubscriptionPackagePlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('price', models.FloatField(default=0.0, verbose_name='Subscription Price')),
                ('package_plan', models.CharField(choices=[('month', 'Month'), ('half-year', 'Six-Month'), ('year', 'Year')], max_length=255, verbose_name='Subscription plan')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserSelectedCourses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, verbose_name='Vehicle Name')),
                ('trainer_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Trainer Name')),
                ('vehicle_registration_no', models.CharField(max_length=100, unique=True, verbose_name='Registration Number')),
                ('license_number', models.CharField(max_length=100, unique=True, verbose_name='License Number')),
                ('vehicle_model', models.CharField(max_length=100, verbose_name='Vehicle Model')),
                ('image', models.ImageField(blank=True, null=True, upload_to='vehicle_images/', verbose_name='Vehicle Image')),
                ('booking_status', models.CharField(choices=[('free', 'Free'), ('booked', 'Booked')], default='free', max_length=10, verbose_name='Vehcile Status')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
    ]
