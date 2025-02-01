from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import redirect  # Импортируем функцию redirect

urlpatterns = [
    # Перенаправление с корня сайта на /admin
    path('', lambda request: redirect('admin:index'), name='home'),

    # Маршрут для стандартной админки Django
    path('admin/', admin.site.urls),

    # Подключение маршрутов приложения payroll
    path('payroll/', include('payroll.urls')),  # Маршруты payroll
]

# Добавление статических файлов только в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Если используются медиафайлы