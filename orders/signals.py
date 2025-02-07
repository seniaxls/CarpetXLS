# orders/signals.py

from django.db.models.signals import pre_save, post_save, m2m_changed, post_init
from django.dispatch import receiver
from .models import ProductOrder, Order, ProductUnit, SecondProductOrder
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Stage
from django.contrib.auth.models import Group
from .models import Stage, GroupStagePermission

@receiver(post_migrate)
def create_default_product_units(sender, **kwargs):
    if sender.name == 'orders':  # Убедитесь, что сигнал работает только для приложения 'orders'
        for size_numb, size_name, size_name_short in ProductUnit.SIZE_TYPES:
            obj, created = ProductUnit.objects.get_or_create(
                size_numb=size_numb,
                defaults={
                    'size_name': size_name,
                    'size_name_short': size_name_short
                }
            )
            if created:
                print(f"Создана единица измерения: {size_name} ({size_name_short})")
            else:
                print(f"Единица измерения уже существует: {size_name} ({size_name_short})")

@receiver(post_migrate)
def create_default_stages(sender, **kwargs):
    if sender.name == 'orders':  # Убедитесь, что сигнал работает только для приложения 'orders'
        if not Stage.objects.exists():  # Проверяем, есть ли уже данные в таблице
            for name, group_stage, super_stage in Stage.STAGE_TYPES:
                Stage.objects.create(
                    name=name,
                    group_stage=group_stage,
                    super_stage=super_stage
                )
            print("Данные этапов успешно созданы.")

@receiver(post_migrate)
def create_default_groups_and_permissions(sender, **kwargs):
    if sender.name == 'orders':  # Убедитесь, что сигнал работает только для приложения 'orders'
        # Создаем группы пользователей
        groups_to_create = ['Директор', 'Мойщик', 'Оператор']
        for group_name in groups_to_create:
            Group.objects.get_or_create(name=group_name)
            print(f"Группа '{group_name}' успешно создана или уже существует.")

        # Настройка разрешений для группы "Директор"
        director_group, _ = Group.objects.get_or_create(name='Директор')
        stages_for_director = Stage.objects.filter(name__in=['Лид', 'Выбивание'])
        if stages_for_director.exists():
            permission, created = GroupStagePermission.objects.get_or_create(group=director_group)
            permission.stages.set(stages_for_director)
            print("Разрешения для группы 'Директор' успешно созданы или обновлены.")

        washer_group, _ = Group.objects.get_or_create(name='Мойщик')
        stages_for_washer = Stage.objects.filter(name__in=['Грязный-Склад', 'Стирка'])
        if stages_for_washer.exists():
            permission, created = GroupStagePermission.objects.get_or_create(group=washer_group)
            permission.stages.set(stages_for_washer)
            print("Разрешения для группы 'Мойщик' успешно созданы или обновлены.")


@receiver(pre_save, sender=ProductOrder)
def calc_amount(sender, instance, **kwargs):
    if instance.overlock is None:
        instance.overlock = 0
    if instance.allowance is None:
        instance.allowance = 0

@receiver(m2m_changed, sender=ProductOrder.product_add.through)
def handle_product_add_m2m_change(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        instance.update_message()
        instance.save()

@receiver(pre_save, sender=ProductOrder)
def handle_product_order_pre_save(sender, instance, **kwargs):
    instance.update_message()

@receiver(post_init, sender=Order)
def calculate_order_sum(sender, instance, **kwargs):
    instance.order_sum = 0
    if not instance.id:
        return  # Если это новый объект, без ID, то суммирование не требуется
    # Оптимизация запросов с использованием select_related и prefetch_related
    product_orders = ProductOrder.objects.filter(order_id=instance).select_related(
        'product', 'product__product_unit'
    ).prefetch_related('product_add', 'product_add__product_unit')
    for data in product_orders:
        # Расчет стоимости основного продукта
        instance.order_sum += data.product.product_price * data.height * data.width
        # Добавление стоимости окантовки (overlock), если она есть
        if data.overlock:
            instance.order_sum += data.overlock
        # Добавление стоимости припусков (allowance), если они есть
        if data.allowance:
            instance.order_sum += data.allowance
        # Расчет стоимости дополнительных продуктов
        for data2 in data.product_add.all():
            if data2.product_unit.size_numb == 32:
                instance.order_sum += data2.product_price * data.height * data.width
            elif data2.product_unit.size_numb == 0:
                instance.order_sum += data2.product_price
    # Обработка вторых продуктов
    second_product_orders = SecondProductOrder.objects.filter(order_id=instance).select_related('product')
    for data in second_product_orders:
        instance.order_sum += data.product.product_price * data.second_amount


