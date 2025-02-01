from django.db import models

from django.core.validators import RegexValidator






class Client(models.Model):
    phoneNumberRegex = RegexValidator(regex=r"^\+7\d{8,12}$", message='Телефон в формате +79001234567')  # \+7\d{10}
    phone_number = models.CharField(validators=[phoneNumberRegex], max_length=12, default='', verbose_name='Телефон', )
    fio = models.CharField(max_length=200, blank=False, null=True, verbose_name='ФИО')
    comment = models.TextField(blank=True, null=True, verbose_name='Коментарий')
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name='Город', default='г Воронеж')
    street = models.CharField(max_length=50, blank=True, null=True, verbose_name='Улица',default='')
    home = models.CharField(max_length=10, blank=True, null=True, verbose_name='Дом',default='')
    apartment = models.CharField(max_length=10, blank=True, null=True, verbose_name='Квартира',default='')
    entrance = models.CharField(max_length=10, blank=True, null=True, verbose_name='Подъезд',default='')
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name='Адрес')

    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    organization = models.BooleanField(default=False, verbose_name='Организация?')


    def save(self, *args, **kwargs):
        self.address = ''
        if self.city:
            self.address += self.city + ", "
        if self.street:
            self.address += self.street+ ", "
        if self.home:
            self.address += self.home+ ", "
        if self.apartment:
            self.address += "кв " + self.apartment+ ", "
        if self.entrance:
            self.address += "под " + self.entrance


        super(Client, self).save(*args, **kwargs)



    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
    def __str__(self):
        return str(self.fio)


