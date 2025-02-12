# orders/apps.py

from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    verbose_name = 'Заказы'

    def ready(self):
        # Импортируем сигналы, чтобы они были зарегистрированы
        import orders.signals

