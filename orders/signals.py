# orders/signals.py

from django.db.models.signals import pre_save, post_save, m2m_changed, post_init
from django.dispatch import receiver
from .models import ProductOrder, Order, ProductUnit, SecondProductOrder
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Stage
from django.contrib.auth.models import Group, Permission
from .models import Stage, GroupStagePermission

@receiver(post_migrate)
def create_default_product_units(sender, **kwargs):
    if sender.name == 'orders':  # Убедитесь, что сигнал работает только для приложения 'orders'
        if not ProductUnit.objects.exists():
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
        # Список групп и соответствующих этапов
        groups_and_stages = {
            'Управляющий': [
                'Лид', 'Нужен вывоз', 'Отменен', 'Курьер забрал', 'Принят в цех',
                'Грязный-Склад', 'Выбивание', 'Стирка', 'Нужен оверлок', 'Финишка',
                'Чистый-Склад', 'Нужна доставка', 'Везем клиенту', 'Выполнен',
                'Возврат', 'Вывоз возврата', 'Везем возврат', 'Сброс'
            ],
            'Оператор': [
                'Лид', 'Нужен вывоз', 'Отменен',
                'Чистый-Склад', 'Нужна доставка',
                'Выполнен', 'Возврат', 'Вывоз возврата',
            ],
            'Курьер': [
                'Нужен вывоз', 'Курьер забрал', 'Принят в цех',
                'Нужна доставка', 'Везем клиенту', 'Выполнен',
                'Вывоз возврата', 'Везем возврат', 'Возврат на складе'
            ],
            'Мойщик': [
                'Нужен вывоз', 'Принят в цех',
                'Грязный-Склад', 'Выбивание', 'Стирка', 'Нужен оверлок', 'Финишка',
                'Чистый-Склад', 'Нужна доставка', 'Выполнен',
                'Возврат'
            ],
        }

        # Разрешения для каждой группы
        group_permissions = {
            'Оператор': [29, 30, 32, 49, 50, 52, 57, 60, 73, 76],
            'Курьер': [50, 52, 57, 58, 73, 74],
            'Мойщик': [
                29, 30, 32, 49, 50, 52, 57, 58, 59, 60,
                73, 74, 75, 76, 97, 98, 101, 104, 105, 108, 109, 112
            ],
            'Управляющий': [
                12, 16, 29, 30, 32, 34, 38, 49, 50, 52,
                57, 58, 59, 60, 66, 73, 74, 75, 76, 84, 88, 97, 98, 101, 104, 105, 108, 109, 112],
        }

        # Проходим по каждой группе
        for group_name, stage_names in groups_and_stages.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            stages = Stage.objects.filter(name__in=stage_names)

            if stages.exists():
                permission, created = GroupStagePermission.objects.get_or_create(group=group)
                permission.stages.set(stages)

                # Если группа "Оператор", устанавливаем allow_call_status=True
                if group_name == 'Оператор':
                    permission.allow_call_status = True
                    permission.save()
                    print(f"Для группы '{group_name}' установлено allow_call_status=True.")

                print(f"Разрешения для группы '{group_name}' успешно созданы или обновлены.")

                # Добавляем разрешения из словаря group_permissions
                if group_name in group_permissions:
                    permission_ids = group_permissions[group_name]
                    permissions = Permission.objects.filter(id__in=permission_ids)
                    group.permissions.set(permissions)
                    print(f"Добавлены разрешения для группы '{group_name}'.")
            else:
                print(f"Не найдено этапов для группы '{group_name}'.")





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


