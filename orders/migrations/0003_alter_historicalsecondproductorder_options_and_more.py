# Generated by Django 5.1.3 on 2025-02-06 12:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
        ('orders', '0002_alter_productorder_history_user_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicalsecondproductorder',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical Допы', 'verbose_name_plural': 'historical Допы'},
        ),
        migrations.AlterModelOptions(
            name='secondproductorder',
            options={'verbose_name': 'Допы', 'verbose_name_plural': 'Допы'},
        ),
        migrations.AlterField(
            model_name='historicalorder',
            name='stage',
            field=models.ForeignKey(blank=True, db_constraint=False, default=5, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='orders.stage', verbose_name='Этап заказа'),
        ),
        migrations.AlterField(
            model_name='order',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='clients.client', verbose_name='Клиент'),
        ),
        migrations.AlterField(
            model_name='order',
            name='stage',
            field=models.ForeignKey(blank=True, default=5, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='orders.stage', verbose_name='Этап заказа'),
        ),
        migrations.CreateModel(
            name='ProductOrderImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='product_order_images/', verbose_name='Фотография')),
                ('product_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='orders.productorder', verbose_name='Заказ продукта')),
            ],
            options={
                'verbose_name': 'Фотография заказа',
                'verbose_name_plural': 'Фотографии заказов',
            },
        ),
    ]
