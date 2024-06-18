# Generated by Django 5.0.3 on 2024-06-03 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordermanagement', '0051_orderitem_key_product_alter_orderitem_payment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='coupon_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='coupon_code',
            field=models.CharField(blank=True, default='None', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_discount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='discount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20),
        ),
    ]