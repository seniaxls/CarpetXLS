from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order, ProductOrder, ProductAdd
from .models import PayrollRecord
import decimal

def calculate_product_area(product_order):
    width = product_order.width or decimal.Decimal('0.0')
    height = product_order.height or decimal.Decimal('0.0')
    return width * height

def calculate_additional_product_area(additional_product, area):
    if additional_product.product_unit.size_numb == 32:
        return area
    return None

@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance, **kwargs):
    if not instance.stage:
        return

    statuses_to_track = ['Грязный-Склад', 'Выбивание', 'Стирка', 'Финишка']
    if instance.stage.name not in statuses_to_track:
        return

    # Get the user who made the change (assuming you have a way to track this)
    user = instance.user

    for product_order in instance.product_order.all():
        area = calculate_product_area(product_order)

        if instance.stage.name == 'Грязный-Склад':
            PayrollRecord.objects.create(
                user=user,
                order=instance,
                status='Грязный-Склад',
                product_name=product_order.product.product_name,
                area=area
            )

        elif instance.stage.name == 'Выбивание':
            PayrollRecord.objects.create(
                user=user,
                order=instance,
                status='Выбивание',
                product_name=product_order.product.product_name,
                area=area
            )

        elif instance.stage.name == 'Стирка':
            PayrollRecord.objects.create(
                user=user,
                order=instance,
                status='Стирка',
                product_name=product_order.product.product_name,
                area=area
            )
            for additional_product in product_order.product_add.all():
                additional_area = calculate_additional_product_area(additional_product, area)
                if additional_area is not None:
                    PayrollRecord.objects.create(
                        user=user,
                        order=instance,
                        status='Стирка',
                        product_name=product_order.product.product_name,
                        additional_product_name=additional_product.product_name,
                        additional_product_area=additional_area
                    )
                elif additional_product.product_unit.size_numb == 0:
                    PayrollRecord.objects.create(
                        user=user,
                        order=instance,
                        status='Стирка',
                        product_name=product_order.product.product_name,
                        additional_product_name=additional_product.product_name,
                        additional_product_price=additional_product.product_price
                    )
            if product_order.overlock and product_order.overlock > 0:
                PayrollRecord.objects.create(
                    user=user,
                    order=instance,
                    status='Стирка',
                    product_name=product_order.product.product_name,
                    overlock=product_order.overlock
                )
            if product_order.allowance and product_order.allowance > 0:
                PayrollRecord.objects.create(
                    user=user,
                    order=instance,
                    status='Стирка',
                    product_name=product_order.product.product_name,
                    allowance=product_order.allowance
                )

        elif instance.stage.name == 'Финишка':
            PayrollRecord.objects.create(
                user=user,
                order=instance,
                status='Финишка',
                product_name=product_order.product.product_name,
                area=area
            )
            if product_order.overlock and product_order.overlock > 0:
                PayrollRecord.objects.create(
                    user=user,
                    order=instance,
                    status='Финишка',
                    product_name=product_order.product.product_name,
                    overlock=product_order.overlock
                )