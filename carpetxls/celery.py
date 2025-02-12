from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Установите переменную окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carpetxls.settings')

# Создайте экземпляр Celery
app = Celery('carpetxls')

# Загрузите конфигурацию из settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживайте задачи в приложениях
app.autodiscover_tasks()