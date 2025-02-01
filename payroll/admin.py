from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from .models import PayrollRecord
from .views import payroll_summary

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
                    'additional_product_area', 'additional_product_price', 'overlock', 'allowance')
    search_fields = ('user__username', 'order__order_number', 'product_name', 'additional_product_name')
    list_filter = ('status', 'user')

    fieldsets = (
        (None, {
            'fields': ('user', 'order', 'status')
        }),
        ('Product Details', {
            'fields': ('product_name', 'area'),
            'classes': ('collapse',),
        }),
        ('Additional Product Details', {
            'fields': ('additional_product_name', 'additional_product_area', 'additional_product_price'),
            'classes': ('collapse',),
        }),
        ('Overlock Details', {
            'fields': ('overlock',),
            'classes': ('collapse',),
        }),
        ('Allowance Details', {
            'fields': ('allowance',),
            'classes': ('collapse',),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Если объект уже существует, сделаем некоторые поля только для чтения
            return self.readonly_fields + ('user', 'order', 'status')
        return self.readonly_fields

# Регистрация модели PayrollRecord в кастомной админке
admin_site.register(PayrollRecord, PayrollRecordAdmin)