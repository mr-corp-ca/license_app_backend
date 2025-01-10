# Generated by Django 4.2.17 on 2025-01-08 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management_app', '0003_transactionhistroy_transaction_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactionhistroy',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='transactionhistroy',
            name='transaction_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('Accepedt', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=15),
        ),
        migrations.AlterField(
            model_name='transactionhistroy',
            name='transaction_type',
            field=models.CharField(choices=[('deposit', 'Deposit'), ('withdraw', 'Withdraw')], max_length=15),
        ),
    ]
