from django.db import models
from django.core.validators import RegexValidator
from django.db import transaction
import re
import re
from django.core.exceptions import ValidationError
from django.db import models

def validate_russian_phone(value):
    # Регулярное выражение для проверки формата номера телефона
    pattern = r'^\+7\d{10}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Номер телефона должен быть в формате +7XXXXXXXXXX (например, +79123456789).'
        )

class Client(models.Model):
    phone_number = models.CharField(
        max_length=12,  # +7 и 10 цифр = 12 символов
        validators=[validate_russian_phone],
        unique=True,
        verbose_name='Телефон')  # Добавлен unique для предотвращения дублирования номеров
    fio = models.CharField(max_length=200, blank=False, null=True, verbose_name='ФИО')
    comment = models.TextField(blank=True, null=True, verbose_name='Коментарий')
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name='Город', default='г Воронеж')
    street = models.CharField(max_length=50, blank=True, null=True, verbose_name='Улица', default='')
    home = models.CharField(max_length=10, blank=True, null=True, verbose_name='Дом', default='')
    apartment = models.CharField(max_length=10, blank=True, null=True, verbose_name='Квартира', default='')
    entrance = models.CharField(max_length=10, blank=True, null=True, verbose_name='Подъезд', default='')
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name='Адрес')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    organization = models.BooleanField(default=False, verbose_name='Организация?')

    def save(self, *args, **kwargs):
        # Используем транзакцию для защиты от состояния гонки
        with transaction.atomic():
            # Блокировка объекта для предотвращения двойной записи
            if self.pk:
                Client.objects.select_for_update().get(pk=self.pk)

            # Формирование адреса
            address_parts = []
            if self.city:
                address_parts.append(self.city)
            if self.street:
                address_parts.append(self.street)
            if self.home:
                address_parts.append(self.home)
            if self.apartment:
                address_parts.append(f"кв {self.apartment}")
            if self.entrance:
                address_parts.append(f"под {self.entrance}")

            # Объединяем части адреса через запятую
            self.address = ", ".join(address_parts)

            super(Client, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        indexes = [
            # Индекс для оптимизации частых запросов по полю phone_number
            models.Index(fields=['phone_number'], name='client_phone_number_idx'),
            # Индекс для оптимизации запросов по полю created_date
            models.Index(fields=['created_date'], name='client_created_date_idx'),
        ]

    def __str__(self):
        return str(self.fio)