from django.apps import AppConfig

class CashRegisterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cash_register'
    verbose_name = 'Кассовый учет'

    def ready(self):
        import cash_register.signals