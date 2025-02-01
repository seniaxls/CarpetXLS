

from django import forms
from django.contrib.auth.models import User
from datetime import date
import calendar
from orders.models import Stage, Product, ProductAdd
from payroll.models import PayrollRecord


class PayrollFilterForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label='Пользователь', required=False)
    year = forms.ChoiceField(choices=[(year, year) for year in range(2024, date.today().year + 1)], label='Год', required=False)
    month = forms.ChoiceField(choices=[(str(month).zfill(2), f'{month} {calendar.month_name[month]}') for month in range(1, 13)], label='Месяц', required=False)
    status = forms.ModelChoiceField(queryset=Stage.objects.none(), label='Статус', required=False)
    product_name = forms.ModelChoiceField(queryset=Product.objects.all(), label='Название продукта', required=False)
    additional_product_name = forms.ModelChoiceField(queryset=ProductAdd.objects.all(), label='Дополнительное название продукта', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for horizontal layout of forms
        self.fields['user'].widget.attrs.update({'class': 'form-control'})
        self.fields['year'].widget.attrs.update({'class': 'form-control'})
        self.fields['month'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
        self.fields['product_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['additional_product_name'].widget.attrs.update({'class': 'form-control'})

        # Populate queryset for status field only with statuses present in PayrollRecord
        statuses = PayrollRecord.objects.values_list('status', flat=True).distinct()
        self.fields['status'].queryset = Stage.objects.filter(name__in=statuses)

    def clean(self):
        cleaned_data = super().clean()
        year = cleaned_data.get('year')
        month = cleaned_data.get('month')

        if year and month:
            try:
                int(year)
                int(month)
            except ValueError:
                raise forms.ValidationError("Некорректные данные для года или месяца.")
        return cleaned_data