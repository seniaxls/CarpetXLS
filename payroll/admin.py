#payroll\armin.py

from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from .models import PayrollRecord
from .views import payroll_summary
from django.urls import reverse

class PayrollAdminSite(admin.AdminSite):
    site_header = "Payroll Administration"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('payroll-summary/', self.admin_view(payroll_summary), name='payroll-summary'),
        ]
        return custom_urls + urls

admin_site = PayrollAdminSite(name='payroll_admin')

# Зарегистрируем модели как обычно
@admin.register(PayrollRecord)
class PayrollRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'order', 'status', 'product_name', 'area', 'additional_product_name',
                     'additional_product_price',  )
    search_fields = ('user__username', 'order__order_number', 'product_name', 'additional_product_name')
    list_filter = ('status', 'user')

    def changelist_view(self, request, extra_context=None):
        # Добавляем кнопку в контекст
        extra_context = extra_context or {}
        extra_context['show_summary_button'] = True
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('payroll-summary/', self.admin_site.admin_view(self.payroll_summary_redirect), name='payroll-summary-redirect'),
        ]
        return custom_urls + urls

    def payroll_summary_redirect(self, request):
        # Перенаправляем на страницу сводки зарплат
        return HttpResponseRedirect(reverse('payroll-summary'))

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Если объект уже существует, сделаем некоторые поля только для чтения
            return self.readonly_fields + ('user', 'order', 'status')
        return self.readonly_fields

# Регистрация модели PayrollRecord в кастомной админке
admin_site.register(PayrollRecord, PayrollRecordAdmin)