# Generated by Django 5.0.3 on 2024-05-24 06:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0027_wallet_last_updated'),
        ('ordermanagement', '0044_remove_order_address_alter_orderitem_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='customer.useraddress'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='payment_status',
            field=models.CharField(choices=[('failed', 'Failed'), ('completed', 'Completed'), ('pending', 'Pending')], default='pending', max_length=20),
        ),
    ]
