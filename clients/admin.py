from django.contrib import admin
from .models import Client


class PhoneEditor(admin.ModelAdmin):
    # Скрываем модель с главной страницы админки только для обычных пользователей
    def has_module_permission(self, request):
        return request.user.is_superuser  # Только суперпользователи видят модель

    list_display = ['phone_number', 'fio', 'city', 'street', 'home', 'apartment', 'entrance']
    list_display_links = ['fio', 'phone_number']  # Убраны дублирующиеся поля
    search_fields = ['phone_number', 'address', 'fio']
    change_form_template = "admin/clients/Client/change_form.html"

    # Оптимизация полей для разных типов пользователей
    def get_fields(self, request, obj=None):
        base_fields = ('phone_number', 'fio', 'comment', 'city', 'street', 'home', 'apartment', 'entrance')
        if request.user.is_superuser:
            return base_fields + ('organization', 'address')  # Добавляем дополнительные поля для суперпользователя
        return base_fields

    # Оптимизация запросов через select_related для связанных моделей (если будут добавлены)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()  # Подгружаем связанные объекты, если они есть

    # Добавляем фильтры для удобства поиска
    list_filter = ['organization', 'created_date']

    # Пагинация для улучшения производительности на больших объемах данных
    list_per_page = 25


# Регистрация модели в админке
admin.site.register(Client, PhoneEditor)