# Generated by Django 4.2.17 on 2025-02-11 17:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course_management_app', '0011_rename_stripe_secret_id_selectedsubscriptionpackagepaln_stripe_secret_id'),
        ('user_management_app', '0013_alter_discountcoupons_package'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discountcoupons',
            name='package',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Subscribed_Package', to='course_management_app.subscriptionpackageplan', verbose_name='Selected Subscription'),
        ),
    ]
