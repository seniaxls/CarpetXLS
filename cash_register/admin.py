from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Shift, Receipt, Refund, CashExpense

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'status', 'opening_time', 'initial_cash', 'closing_time',
        'total_sales', 'total_refunds', 'total_expenses'
    )
    readonly_fields = (
        'opening_time', 'closing_time', 'initial_cash', 'final_cash',
        'total_sales', 'total_cash', 'total_non_cash', 'total_refunds',
        'total_expenses'
    )

    def get_readonly_fields(self, request, obj=None):
        # Если смена уже существует и имеет статус 'closed', делаем все поля только для чтения
        if obj and obj.status == 'closed':
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def save_model(self, request, obj, form, change):
        try:
            # Если это новая смена, устанавливаем initial_cash и total_cash
            if not obj.id and obj.status == 'open':
                last_closed_shift = Shift.objects.filter(status='closed').order_by('-closing_time').first()
                if last_closed_shift:
                    obj.initial_cash = last_closed_shift.final_cash or 0
                    obj.total_cash = obj.initial_cash
            obj.save()
        except ValidationError as e:
            self.message_user(request, f"Ошибка при сохранении смены: {e}", level='error')

    def has_change_permission(self, request, obj=None):
        # Запрещаем изменение закрытой смены
        if obj and obj.status == 'closed':
            return False
        return super().has_change_permission(request, obj)

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'shift', 'payment_method', 'amount')
    list_filter = ('payment_method', )
    readonly_fields = ('created_at', 'amount', 'shift')
    search_fields=['id','order__id','amount']

    def clean(self):
        cleaned_data = super().clean()
        order = cleaned_data.get('order')

        # Проверяем наличие открытой смены
        if not Shift.objects.filter(status='open').exists():
            raise ValidationError("Нет открытой смены для создания чека.")

        # Дополнительные проверки (если нужны)
        if order and order.stage.group_stage != 7:
            raise ValidationError("Чек можно создать только для заказа с статусом ['Нужна доставка','Везем клиенту', 'Выполнен']")

        return cleaned_data

    def has_change_permission(self, request, obj=None):
        # Запрещаем редактирование чеков после создания
        return False

    def save_model(self, request, obj, form, change):
        try:
            obj.save()
        except ValidationError as e:
            self.message_user(request, f"Ошибка при сохранении чека: {e}", level='error')

    def has_module_permission(self, request):
        # Скрываем модель с главной страницы админки только для обычных пользователей
        if request.user.is_superuser:
            return True  # Суперпользователи видят модель
        return False  # Обычные пользователи не видят модель

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('id', 'receipt', 'refunded_at', 'amount', 'payment_method', 'shift')
    readonly_fields = ('refunded_at', 'amount', 'payment_method', 'shift')
    search_fields = ['id', 'receipt__order__id', 'amount', 'receipt__id']

    def save_model(self, request, obj, form, change):
        try:
            obj.save()
        except ValidationError as e:
            self.message_user(request, f"Ошибка при сохранении возврата: {e}", level='error')
        except Exception as e:
            self.message_user(request, f"Неизвестная ошибка: {e}", level='error')

    def has_change_permission(self, request, obj=None):
        # Запрещаем редактирование возвратов после создания
        return False

@admin.register(CashExpense)
class CashExpenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'shift', 'amount', 'created_at')
    readonly_fields = ('created_at',)

    def has_change_permission(self, request, obj=None):
        # Запрещаем редактирование документов расхода после создания
        return False

    def save_model(self, request, obj, form, change):
        try:
            obj.save()
        except ValidationError as e:
            self.message_user(request, f"Ошибка при сохранении расхода: {e}", level='error')



