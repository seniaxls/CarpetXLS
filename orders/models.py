
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, post_init, pre_init, m2m_changed
from django.dispatch import receiver
from django import utils
from clients.models import Client
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.utils import timezone


class ProductUnit(models.Model):
    SIZE_TYPES = (
        (0, "Штуки", "шт"),
        (11, "Килограмм", "кг"),
        (20, "Сантиметр", "см"),
        (22, "Метр", "м"),
        (32, "Квадратный метр", "м²"),
    )

    size_numb = models.IntegerField(verbose_name='ID', default=0, blank=True)
    size_name = models.CharField(max_length=20, default="Штуки", blank=True)
    size_name_short = models.CharField(max_length=3, default="шт", blank=True)

    class Meta:
        verbose_name = 'Единицы измерения'
        verbose_name_plural = 'Единицы измерения'

    def __str__(self):
        return '{}'.format(self.size_name)

class SecondProduct(models.Model):
    product_name = models.CharField(max_length=100, verbose_name='Название услуги', default="Стирка пледа")
    product_long_name = models.CharField(max_length=100, verbose_name='Название услуги', default="Стирка пледа")
    product_unit = models.ForeignKey(ProductUnit, models.SET_NULL, null=True, verbose_name='Единица измерения', default=1  )
    product_price = models.IntegerField(verbose_name='Цена', default=100)
    min_amount = models.DecimalField(max_digits=3, decimal_places=1, default=1, verbose_name='Минимальное Кол-во')

    class Meta:
        verbose_name = 'Услуги стирки'
        verbose_name_plural = 'Услуги стирки'

    def __str__(self):
        return "{} ({}₽{})".format(self.product_name,self.product_price, self.product_unit.size_name_short)

class Product(models.Model):
    product_name = models.CharField(max_length=100, verbose_name='Название услуги', default="Короткий ворс")
    product_long_name = models.CharField(max_length=100, verbose_name='Название услуги', default="Короткий ворс")
    product_unit = models.ForeignKey(ProductUnit, models.SET_NULL, null=True, verbose_name='Единица измерения', default=1  )
    product_price = models.IntegerField(verbose_name='Цена', default=150)
    min_amount = models.DecimalField(max_digits=3, decimal_places=1, default=1, verbose_name='Минимальное Кол-во')

    class Meta:
        verbose_name = 'Услуги стирки ковров'
        verbose_name_plural = 'Услуги стирки ковров'

    def __str__(self):
        return "{} ({}₽{})".format(self.product_name,self.product_price, self.product_unit.size_name_short)

class ProductAdd(models.Model):
    product_name = models.CharField(max_length=100, verbose_name='Название услуги', default="Запах")
    product_long_name = models.CharField(max_length=100, verbose_name='Название услуги', default="Запах")
    product_unit = models.ForeignKey(ProductUnit, models.SET_NULL, null=True, verbose_name='Единица измерения', default=1  )
    product_price = models.IntegerField(verbose_name='Цена', default=100)
    min_amount = models.DecimalField(max_digits=3, decimal_places=1, default=1, verbose_name='Минимальное Кол-во')

    class Meta:
        verbose_name = 'Доп услуги стирки ковров'
        verbose_name_plural = 'Доп услуги стирки ковров'

    def __str__(self):
        return "{} ({}₽{})".format(self.product_name,self.product_price, self.product_unit.size_name_short)

class Stage(models.Model):
    STAGE_TYPES = (
        ('Лид', 1, False),
        ('Нужен вывоз', 1, False),
        ('Отменен', 1, False),
        ('Курьер забрал', 1, False),
        ('Принят в цех', 1, True),
        ('Грязный-Склад', 2, True),
        ('Выбивание', 3, True),
        ('Стирка', 4, True),
        ('Финишка', 5, True),
        ('Нужен оверлок', 6, False),
        ('Чистый-Склад', 6, True),
        ('Нужна доставка', 7, False),
        ('Везем клиенту', 7, False),
        ('Выполнен', 7, True),
        ('Возврат', 8, True),
        ('Вывоз возврата', 8, True),
        ('Везем возврат', 8, True),
        ('Сброс', 9, True),
    )

    name = models.CharField(max_length=50, unique=True, verbose_name="Название этапа")
    group_stage = models.PositiveIntegerField(verbose_name="Группа этапов", help_text="Номер группы, к которой относится этап")
    super_stage = models.BooleanField(default=False, verbose_name="Супер-этап")
    first_message = models.TextField(blank=True, null=True, verbose_name="Сообщение")
    second_message = models.TextField(blank=True, null=True, verbose_name="Сообщение 2")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Этап"
        verbose_name_plural = "Этапы"
        ordering = ['id']  # Сортировка по PK (id) от меньшего к большему

class Order(models.Model):
    order_number = models.CharField(max_length=10, editable=False, verbose_name='Номер заказа')
    stage = models.ForeignKey(
        Stage,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name="Этап заказа",
        null=True,  # Разрешаем NULL
        blank=True  # Разрешаем пустой выбор
    )
    check_call = models.BooleanField(default=False, verbose_name="Позвонить")
    client = models.ForeignKey(Client, models.SET_NULL, blank=True, null=True, verbose_name='Клиент')
    target_date = models.DateField(blank=True, null=True, verbose_name='Целевая дата')
    order_sum = models.DecimalField(default=0, verbose_name='Сумма заказа', decimal_places=2, max_digits=7)
    comment = models.TextField(default=None, verbose_name='Комментарий', blank=True)
    create_date = models.DateField(auto_now_add=True, verbose_name='Дата создания')
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата обновления", auto_now=True)
    create_date_time = models.DateTimeField(auto_created=True, verbose_name='Дата время создания', default=timezone.now)

    def __str__(self):
        return f"Заказ #{self.order_number or 'Без номера'}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    @staticmethod
    def get_available_stages(user, obj=None):
        # Определяем разрешенные этапы для пользователя
        accessible_stage_ids = set(GroupStagePermission.get_accessible_stages(user))
        if obj is None:
            # При создании нового заказа доступна только первая группа этапов
            return Stage.objects.filter(group_stage=1, id__in=accessible_stage_ids)
        current_stage = obj.stage
        # Добавляем текущий этап в список доступных
        available_stage_ids = {current_stage.id}
        # Определяем текущую группу этапов
        current_group = current_stage.group_stage
        # Если текущий этап является супер-этапом, добавляем этапы из следующей группы
        if current_stage.super_stage:
            next_group = current_group + 1
            next_group_stages = Stage.objects.filter(group_stage=next_group, id__in=accessible_stage_ids)
            available_stage_ids.update(next_group_stages.values_list('id', flat=True))
        else:
            # Иначе добавляем все этапы из текущей группы
            current_group_stages = Stage.objects.filter(group_stage=current_group, id__in=accessible_stage_ids)
            available_stage_ids.update(current_group_stages.values_list('id', flat=True))
        # Для суперпользователя доступны все этапы, но они остаются организованными по группам
        if user.is_superuser:
            return Stage.objects.filter(id__in=available_stage_ids)
        return Stage.objects.filter(id__in=available_stage_ids)

    def save(self, *args, **kwargs):
        # Автоматическая генерация номера заказа
        if not self.order_number:
            last_order = Order.objects.all().last()
            self.order_number = f"{(last_order.id + 1):03d}" if last_order else "001"

        # Проверяем, имеет ли пользователь право на выбранный этап
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = kwargs.pop('user', None) or getattr(self, '_user', None)
        if user and not user.is_superuser:
            accessible_stage_ids = set(GroupStagePermission.get_accessible_stages(user))
            if self.stage_id and self.stage_id not in accessible_stage_ids:
                raise PermissionDenied(f"У вас нет прав на установку этапа '{self.stage.name}'.")

        # Автоматическое изменение этапа с 'Сброс' на 'Принят в цех'
        reset_stage = Stage.objects.filter(name='Сброс').first()
        accepted_in_workshop_stage = Stage.objects.filter(name='Принят в цех').first()
        if reset_stage and accepted_in_workshop_stage and self.stage == reset_stage:
            self.stage = accepted_in_workshop_stage
            print("Этап заказа автоматически изменен с 'Сброс' на 'Принят в цех'.")

        # Автоматическая установка флага 'Позвонить' для определённых этапов
        stages_with_check_call = Stage.objects.filter(
            name__in=['Нужен вывоз', 'Чистый-Склад', 'Нужна доставка', 'Вывоз возврата']
        ).values_list('id', flat=True)

        # Проверяем, был ли флаг check_call изменён вручную
        if self.stage_id in stages_with_check_call:
            # Устанавливаем флаг только если он не был снят вручную
            if not hasattr(self, '_manual_check_call_change'):
                self.check_call = True
                print(f"Флаг 'Позвонить' автоматически установлен для этапа '{self.stage.name}'.")
        elif self.stage and self.stage.name not in ['Нужен вывоз', 'Чистый-Склад', 'Нужна доставка', 'Вывоз возврата']:
            # Сбрасываем флаг, если этап изменился на другой
            if not hasattr(self, '_manual_check_call_change'):
                self.check_call = False

        super().save(*args, **kwargs)

class GroupStagePermission(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Группа пользователей")
    stages = models.ManyToManyField(Stage, related_name='group_permissions', verbose_name="Доступные этапы")
    days_limit = models.PositiveIntegerField(
        default=30,
        verbose_name="Количество последних дней",
        help_text="Количество дней, за которые будут выводиться заказы. 0 = без ограничений."
    )

    def __str__(self):
        return f"{self.group.name} - {', '.join([stage.name for stage in self.stages.all()])}"

    class Meta:
        verbose_name = "Разрешение на этапы"
        verbose_name_plural = "Разрешения на этапы"

    @staticmethod
    def get_accessible_stages(user):
        """
        Возвращает список ID этапов, доступных для пользователя.
        """
        if user.is_superuser:
            # Суперпользователь видит все этапы
            return Stage.objects.values_list('id', flat=True)

        group_ids = user.groups.values_list('id', flat=True)
        accessible_stages = GroupStagePermission.objects.filter(group_id__in=group_ids).values_list('stages', flat=True)
        return list(accessible_stages)

    @staticmethod
    def get_days_limit(user):
        """
        Возвращает количество дней для фильтрации заказов.
        Если days_limit=0, возвращается None (без ограничений).
        """
        if user.is_superuser:
            # Суперпользователь видит все заказы без ограничений
            return None

        group_ids = user.groups.values_list('id', flat=True)
        permissions = GroupStagePermission.objects.filter(group_id__in=group_ids)
        if permissions.exists():
            # Берем минимальное значение days_limit среди всех разрешений пользователя
            days_limit = min(permission.days_limit for permission in permissions)
            return None if days_limit == 0 else days_limit
        return 30  # Значение по умолчанию

class ProductOrder(models.Model):
    message = models.TextField(verbose_name='Сообщение', blank=True)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ', related_name='product_order')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=None, verbose_name='Наименование')
    width = models.DecimalField(max_digits=4, decimal_places=2, default=1, verbose_name='Ширина', validators=[MaxValueValidator(19), MinValueValidator(0.1)])
    height = models.DecimalField(max_digits=4, decimal_places=2, default=1, verbose_name='Длина', validators=[MaxValueValidator(19), MinValueValidator(0.1)])
    product_add = models.ManyToManyField(ProductAdd, default=None, blank=True, verbose_name='Доп услуги',related_name='product_add')
    overlock = models.DecimalField(max_digits=5, decimal_places=2,validators=[MaxValueValidator(9999), MinValueValidator(0)], default=None, verbose_name='Оверлок', blank=True, null=True)
    allowance = models.DecimalField(max_digits=5, decimal_places=2,validators=[MaxValueValidator(9999), MinValueValidator(0)], default=None, verbose_name='Надбавка', blank=True, null=True)
    comment = models.TextField( verbose_name='Комментарий', blank=True)


    def update_message(self):
        self.message = ''

        # Инициализация переменных
        total_sum = 0
        unit = self.product.product_unit.size_name_short
        base_price = self.product.product_price
        area = float(self.width) * float(self.height)
        total_price = base_price * area

        # Формирование строки сообщения
        message_lines = [
            f"{self.product.product_name}: {'%.2f' % self.height} x {'%.2f' % self.width} {unit}",
            f"{'%.2f' % area}{unit} * {'%.0f' % base_price}₽ = {'%.0f' % total_price}₽"
        ]

        total_sum += total_price

        # Обработка дополнительных продуктов



        # Обработка оверлока
        if self.overlock is not None:
            total_sum += float(self.overlock)
            message_lines.append(f"Оверлок: {'%.0f' % self.overlock}₽")

        # Обработка доплаты
        if self.allowance is not None:
            total_sum += float(self.allowance)
            message_lines.append(f"Дополнительно: {'%.0f' % self.allowance}₽")

        # Итоговая сумма


        # Обновляем поле message, если объект уже сохранен в базе данных
        if self.pk:
            for additional_product in self.product_add.all():
                if additional_product.product_unit.size_numb == 32:
                    additional_price = area * additional_product.product_price
                    total_sum += additional_price
                    message_lines.append(f"{additional_product.product_name}: {'%.0f' % additional_price}₽")
                elif additional_product.product_unit.size_numb == 0:
                    additional_price = additional_product.product_price
                    total_sum += additional_price
                    message_lines.append(f"{additional_product.product_name}: {'%.0f' % additional_price}₽")

            message_lines.append(f"Итого: {'%.0f' % total_sum}₽")
            # Соединяем все строки в одно сообщение
            final_message = "\n".join(message_lines)
            self.message = final_message

    def save(self, *args, **kwargs):
        # Если это новый объект и он еще не сохранен, то сохраняем его без связей Many-to-Many
        if not self.pk:
            super().save(*args, **kwargs)
            # После сохранения можно установить связи Many-to-Many
            if hasattr(self, '_temp_product_add'):
                self.product_add.set(self._temp_product_add)
                delattr(self, '_temp_product_add')
                self.update_message()  # Пересчитываем стоимость и обновляем сообщение
                super().save(*args, **kwargs)
        else:
            self.update_message()  # Пересчитываем стоимость и обновляем сообщение до сохранения
            super().save(*args, **kwargs)

    def __str__(self):

        return ''

    class Meta:
        verbose_name = 'Ковер'
        verbose_name_plural = 'Ковры'

class MessageProductOrder(models.Model):
    product_order = models.ForeignKey(ProductOrder, on_delete=models.CASCADE, default=None, related_name="mesage_order")
    message = models.TextField(verbose_name='Наименование', blank=True,)

class SecondProductOrder(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    product = models.ForeignKey(SecondProduct, verbose_name='Наименование', default=None, on_delete=models.CASCADE)
    second_amount = models.DecimalField(max_digits=4, decimal_places=2, default=1, verbose_name='Кол-во',validators=[MaxValueValidator(99), MinValueValidator(0)])

    def __str__(self):
        return ""

    class Meta:
        verbose_name = 'Стирка'
        verbose_name_plural = 'Стирка'



@receiver(pre_save, sender=ProductOrder)
def calc_amount(sender, instance, **kwargs):
    if instance.overlock == None:
        instance.overlock = 0
    if instance.allowance == None:
        instance.allowance = 0

def set_product_add(instance, product_add_list):
    if instance.pk is None:
        # Если объект еще не сохранен, временно храним связанные объекты
        instance._temp_product_add = product_add_list
    else:
        # Если объект уже сохранен, можно сразу установить связи Many-to-Many
        instance.product_add.set(product_add_list)
        instance.update_message()  # Пересчитываем стоимость и обновляем сообщение
        instance.save()

# Регистрация сигнала m2m_changed для связи product_add в модели ProductOrder
@receiver(m2m_changed, sender=ProductOrder.product_add.through)
def handle_product_add_m2m_change(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        # После изменения связей Many-to-Many, пересчитываем стоимость и обновляем сообщение
        instance.update_message()
        instance.save()

# Регистрация сигнала pre_save для модели ProductOrder
@receiver(pre_save, sender=ProductOrder)
def handle_product_order_pre_save(sender, instance, **kwargs):
    instance.update_message()




@receiver(pre_save, sender=Order)
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



