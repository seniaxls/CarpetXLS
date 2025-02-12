from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import redirect  # Импортируем функцию redirect
from orders import views
from django.http import JsonResponse

def test_headers_view(request):
    # Получаем значение заголовка X-Requested-With
    x_requested_with = request.headers.get('X-Requested-With', 'Not Provided')
    return JsonResponse({'X-Requested-With': x_requested_with})


urlpatterns = [
    # Перенаправление с корня сайта на /admin
    path('', lambda request: redirect('admin:index'), name='home'),

    # Маршрут для стандартной админки Django
    path('admin/', admin.site.urls),

    # Подключение маршрутов приложения payroll
    path('payroll/', include('payroll.urls')),  # Маршруты payroll

    path('telegram-browser-info/', views.telegram_browser_info, name='telegram_browser_info'),

    path('test-headers/', test_headers_view, name='test_headers'),


]

# Добавление статических файлов только в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Если используются медиафайлы