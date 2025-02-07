from django.apps import AppConfig

class PayrollConfig(AppConfig):
    name = 'payroll'
    verbose_name = 'Начисления для расчета ЗП'

    def ready(self):
        import payroll.signals