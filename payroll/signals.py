from simple_history.utils import get_history_manager_for_model
from django.db.models.signals import post_save, pre_save
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

@receiver(pre_save, sender=Order)
def track_previous_stage(sender, instance, **kwargs):
    """
    Track the previous stage of the Order instance before saving.
    """
    if instance.pk:  # Check if the instance already exists in the database
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._previous_stage = old_instance.stage
        except Order.DoesNotExist:
            instance._previous_stage = None
    else:
        instance._previous_stage = None


@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance, **kwargs):
    """
    Handle order status change and create PayrollRecord entries only if the stage has changed.
    """
    # Check if the stage has changed
    previous_stage = getattr(instance, '_previous_stage', None)
    if not previous_stage or previous_stage == instance.stage:
        return  # No change in stage, exit early

    statuses_to_track = ['Грязный-Склад', 'Выбивание', 'Стирка', 'Финишка']
    if instance.stage.name not in statuses_to_track:
        return

    history_manager = get_history_manager_for_model(Order)
    latest_history = history_manager.filter(id=instance.id).first()
    user = latest_history.history_user if latest_history else None

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
                        area=additional_area
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

            if product_order.allowance and product_order.allowance > 0:
                PayrollRecord.objects.create(
                    user=user,
                    order=instance,
                    status='Стирка',
                    product_name=product_order.product.product_name,
                    additional_product_name='Доп суммой',
                    additional_product_price=product_order.allowance
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
                    additional_product_name='Оверлок',
                    additional_product_price=product_order.overlock,

                )