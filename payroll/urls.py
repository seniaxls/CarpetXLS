from django.urls import path
from .admin import admin_site  # Импортируем кастомную админку
from .views import payroll_summary  # Импортируем представление payroll_summary

urlpatterns = [
    # Добавляем маршрут для страницы payroll-summary
    path('payroll-summary/', admin_site.admin_view(payroll_summary), name='payroll-summary'),

    # Маршрут для подключения кастомной админки
    path('payroll-admin/', admin_site.urls),
]