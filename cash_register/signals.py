from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Receipt, Refund, Shift, CashExpense



@receiver(post_delete, sender=CashExpense)
def update_shift_on_cash_expense_delete(sender, instance, **kwargs):
    shift = instance.shift
    shift.total_cash = (shift.total_cash or 0) + instance.amount
    shift.total_expenses -= instance.amount
    shift.save()

@receiver(post_save, sender=Receipt)
def update_shift_on_receipt_save(sender, instance, created, **kwargs):
    if created:
        shift = instance.shift
        if instance.payment_method == 'cash':
            shift.total_cash = (shift.total_cash or 0) + instance.amount
        else:
            if instance.payment_method != 'org_transfer':
                shift.total_non_cash = (shift.total_non_cash or 0) + instance.amount
        if instance.payment_method != 'org_transfer':
            shift.total_sales = (shift.total_sales or 0) + instance.amount
            shift.save()
        else:
            shift.save()

