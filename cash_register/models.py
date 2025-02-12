from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.contrib.auth.models import User

class PaymentMethod(models.TextChoices):
    CASH = 'cash', 'Наличные'
    CARD = 'card', 'Карта'
    TRANSFER = 'transfer', 'Перевод'
    ORGANIZATION_TRANSFER = 'org_transfer', 'Перевод организации'

class Shift(models.Model):
    STATUS_CHOICES = (
        ('open', 'Открыта'),
        ('closed', 'Закрыта'),
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='open',
        verbose_name="Статус"
    )
    opening_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время открытия"
    )
    closing_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Время закрытия"
    )
    initial_cash = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Наличные на начало дня",
        editable=False
    )
    final_cash = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Наличные на конец дня",
        editable=False
    )
    total_sales = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Общая выручка нал + безнал",
        editable=False
    )
    total_cash = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="В Кассе",
        editable=False
    )
    total_non_cash = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Выручка безналичными",
        editable=False
    )
    total_refunds = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Общая сумма возвратов",
        editable=False
    )
    total_expenses = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Общий расход наличных",
        editable=False
    )

    class Meta:
        verbose_name = "Смена"
        verbose_name_plural = "Смены"

    def clean(self):
        # Проверяем, что только одна смена может быть открыта
        if self.status == 'open' and Shift.objects.filter(status='open').exclude(id=self.id).exists():
            raise ValidationError("Может быть только одна открытая смена.")
        # Запрещаем создание новой смены со статусом "closed"
        if not self.id and self.status == 'closed':
            raise ValidationError("Нельзя создать новую смену со статусом 'Закрыта'.")
        # Нельзя изменить закрытую смену на открытую
        if self.id and self.status == 'open' and Shift.objects.filter(id=self.id, status='closed').exists():
            raise ValidationError("Нельзя изменить закрытую смену на открытую.")

    def save(self, *args, **kwargs):
        # Автоматическое заполнение начальной суммы из предыдущей закрытой смены
        if not self.id and self.status == 'open':
            last_closed_shift = Shift.objects.filter(status='closed').order_by('-closing_time').first()
            if last_closed_shift:
                self.initial_cash = last_closed_shift.final_cash or 0
                self.total_cash = self.initial_cash
        # Автоматическое заполнение данных при закрытии смены
        if self.status == 'closed' and self.id:
            self.closing_time = now()
            self.final_cash = (self.total_cash or 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Смена {self.id}"


class Receipt(models.Model):
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.PROTECT,
        related_name='receipt',
        verbose_name="Заказ"
    )
    shift = models.ForeignKey(
        Shift,
        on_delete=models.PROTECT,
        related_name='receipts',
        verbose_name="Смена",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        verbose_name="Способ оплаты"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма",
        editable=False
    )

    class Meta:
        verbose_name = "Чек"
        verbose_name_plural = "Чеки"


    def clean(self):
        # Проверяем, что смена открыта
        if self.shift and self.shift.status == 'closed':
            raise ValidationError("Нельзя добавить чек в закрытую смену.")
        # Проверяем, что stage_group заказа равен 7
        if self.order.stage.group_stage != 7:
            raise ValidationError("Чек можно создать только для заказа с статусом ['Нужна доставка','Везем клиенту', 'Выполнен']")
        if not self.shift:
            open_shift = Shift.objects.filter(status='open').first()
            if not open_shift:
                raise ValidationError("Нет открытой смены для создания чека.")
            self.shift = open_shift

    def save(self, *args, **kwargs):
        # Запрещаем редактирование существующих чеков
        if self.id:
            raise ValidationError("Редактирование чека запрещено.")
        # Автоматически привязываем текущую открытую смену
        if not self.shift:
            open_shift = Shift.objects.filter(status='open').first()
            if not open_shift:
                raise ValidationError("Нет открытой смены для создания чека.")
            self.shift = open_shift
        # Автоматическое заполнение суммы чека из заказа
        if not self.amount:
            self.amount = self.order.order_sum

        super().save(*args, **kwargs)



    def __str__(self):
        return f""


class Refund(models.Model):
    receipt = models.OneToOneField(
        Receipt,
        on_delete=models.PROTECT,
        related_name='refund',
        verbose_name="Чек"
    )
    refunded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата возврата"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма возврата",
        editable=False
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        verbose_name="Способ возврата",
        editable=False
    )
    shift = models.ForeignKey(
        Shift,
        on_delete=models.PROTECT,
        related_name='refunds',
        verbose_name="Смена",
        editable=False
    )

    class Meta:
        verbose_name = "Возврат"
        verbose_name_plural = "Возвраты"

    def clean(self):
        # Проверяем, что смена чека еще не закрыта
        if self.receipt.shift.status == 'closed':
            raise ValidationError("Нельзя сделать возврат для чека из закрытой смены.")
        # Убедимся, что поле shift заполняется из чека
        if not self.shift_id:
            self.shift = self.receipt.shift
        # Проверяем, достаточно ли средств для возврата
        if self.payment_method == 'cash' and (self.receipt.shift.total_cash or 0) - self.amount < 0:
            raise ValidationError("Недостаточно наличных средств в смене для данного возврата.")

    def save(self, *args, **kwargs):
        # Автоматическое заполнение данных из чека
        if not self.amount:
            self.amount = self.receipt.amount
        if not self.payment_method:
            self.payment_method = self.receipt.payment_method
        if not self.shift_id:
            self.shift = self.receipt.shift
        # Обновляем статистику смены
        shift = self.shift
        if self.payment_method == 'cash':
            shift.total_cash = max((shift.total_cash or 0) - self.amount, 0)
        else:
            if self.payment_method != 'org_transfer':
                shift.total_non_cash = max((shift.total_non_cash or 0) - self.amount, 0)
                shift.total_refunds += self.amount
                shift.save()
        # Сохраняем сам объект возврата
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Возврат для чека {self.receipt.id}"


class CashExpense(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Пользователь"
    )
    shift = models.ForeignKey(
        Shift,
        on_delete=models.PROTECT,
        related_name='cash_expenses',
        verbose_name="Смена"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма расхода"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Наличный расход"
        verbose_name_plural = "Наличные расходы"

    def clean(self):
        # Проверяем, что смена открыта
        if self.shift.status == 'closed':
            raise ValidationError("Нельзя создать расход для закрытой смены.")
        # Проверяем, что сумма не отрицательная
        if self.amount <= 0:
            raise ValidationError("Сумма расхода должна быть больше нуля.")
        # Проверяем, что сумма не превышает доступный остаток наличных в смене
        if (self.shift.total_cash or 0) - self.amount < 0:
            raise ValidationError("Недостаточно наличных средств в смене для данного расхода.")

    def save(self, *args, **kwargs):
        # Запрещаем редактирование существующих записей
        if self.id:
            raise ValidationError("Редактирование документа расхода запрещено.")
        # Вызываем метод clean() для выполнения валидации
        self.clean()
        # Обновляем статистику смены
        shift = self.shift
        shift.total_cash = max((shift.total_cash or 0) - self.amount, 0)
        shift.total_expenses += self.amount
        shift.save()
        # Сохраняем сам объект расхода
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Расход {self.id} на сумму {self.amount}"