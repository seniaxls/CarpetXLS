# Generated by Django 5.1.3 on 2025-02-07 18:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cash_register', '0004_alter_receipt_order'),
        ('orders', '0007_alter_historicalproductorder_allowance_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipt',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='receipt', to='orders.order', verbose_name='Заказ'),
        ),
    ]
