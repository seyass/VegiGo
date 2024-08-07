# Generated by Django 5.0.3 on 2024-04-23 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordermanagement', '0004_alter_order_payment_method_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='payment_status',
            field=models.CharField(choices=[('failed', 'Failed'), ('pending', 'Pending'), ('completed', 'Completed')], default='pending', max_length=20),
        ),
    ]
