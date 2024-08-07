# Generated by Django 5.0.3 on 2024-05-01 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productmanagement', '0016_alter_product_unit_type_alter_productoffer_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoryoffer',
            name='status',
            field=models.CharField(choices=[('expired', 'Expired'), ('active', 'Active'), ('upcoming', 'Upcoming')], default='upcoming', max_length=10),
        ),
        migrations.AddField(
            model_name='productoffer',
            name='status',
            field=models.CharField(choices=[('expired', 'Expired'), ('active', 'Active'), ('upcoming', 'Upcoming')], default='upcoming', max_length=10),
        ),
        migrations.AlterField(
            model_name='product',
            name='unit_type',
            field=models.CharField(choices=[('l', 'L'), ('kg', 'Kg'), ('g', 'G')], default='kg', max_length=10),
        ),
    ]
