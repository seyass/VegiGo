# Generated by Django 5.0.3 on 2024-04-30 03:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productmanagement', '0011_alter_product_unit_type'),
        ('vgadmin', '0002_alter_branches_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='unit_type',
            field=models.CharField(choices=[('g', 'G'), ('l', 'L'), ('kg', 'Kg')], default='kg', max_length=10),
        ),
        migrations.AlterField(
            model_name='productlocations',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vgadmin.branches'),
        ),
    ]
