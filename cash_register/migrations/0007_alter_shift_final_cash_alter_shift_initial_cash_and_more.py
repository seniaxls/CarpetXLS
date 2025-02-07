# Generated by Django 5.1.3 on 2025-02-07 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cash_register', '0006_alter_cashexpense_options_alter_receipt_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shift',
            name='final_cash',
            field=models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=10, null=True, verbose_name='Наличные на конец дня'),
        ),
        migrations.AlterField(
            model_name='shift',
            name='initial_cash',
            field=models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=10, verbose_name='Наличные на начало дня'),
        ),
        migrations.AlterField(
            model_name='shift',
            name='total_cash',
            field=models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=10, verbose_name='В Кассе'),
        ),
        migrations.AlterField(
            model_name='shift',
            name='total_sales',
            field=models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=10, verbose_name='Общая выручка нал + безнал'),
        ),
    ]
