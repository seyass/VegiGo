# Generated by Django 5.0.3 on 2024-05-15 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0023_cart_sub_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='max_quantity',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]