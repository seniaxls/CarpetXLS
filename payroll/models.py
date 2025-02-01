from django.db import models
from orders.models import Order, ProductOrder, Product, ProductAdd
from django.contrib.auth.models import User

class PayrollRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    product_name = models.CharField(max_length=100, null=True, blank=True)
    area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    additional_product_name = models.CharField(max_length=100, null=True, blank=True)
    additional_product_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    additional_product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    overlock = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Запись зарплаты'
        verbose_name_plural = 'Записи зарплат'

    def __str__(self):
        return f"{self.user.username} - {self.status} ({self.order.order_number})"