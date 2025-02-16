"""
Django settings for CarpetXLS project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1w8)@tj$*t)rsoo#h7^ev7mqq@!x1&7!r@8_sduasff_*!q_2_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['carpetxls.ru','localhost',"192.168.1.123",'127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'extra_settings',
    'ClientsCRM.apps.ClientscrmConfig',
    'OrdersCRM.apps.OrderscrmConfig',
    'LogsCRM.apps.LogscrmConfig',
    'CashCRM.apps.CashcrmConfig',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'CarpetXLS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries' : {
                'staticfiles': 'django.templatetags.static', #Added here
            }
        },
    },
]

WSGI_APPLICATION = 'CarpetXLS.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

#DATABASES = {'default': {"ENGINE": "django.db.backends.mysql","NAME": "new_schema","USER": "root","PASSWORD": "123321","HOST": "localhost",}}

DATABASES = {   'default': {"ENGINE": "django.db.backends.mysql","NAME": "a1075116_carpet","USER": "a1075116_carpet","PASSWORD": "gp6L9VKy","HOST": "localhost",}}



# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS  = [os.path.join(BASE_DIR, "static")]

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), "./CarpetXLS/static_cdn")


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'



EXTRA_SETTINGS_DEFAULTS = [
    {
        "name": "DADATA_COORDS_LAT",
        "type": "decimal",
        "value": 50.1982560000,
        "description":"Широта"
    },
    {
            "name": "DADATA_COORDS_LON",
            "type": "decimal",
            "value": 39.5626320000,
            "description":"Долгота"
        },
    {
            "name": "DADATA_RADIUS",
            "type": "int",
            "value": 30000,
            "description":"Радиус"

        },
    {
            "name": "DADATA_TOKEN",
            "type": "string",
            "value": '3d8a698d484a23a8b0d86cd295e31e0c780baeac',
            "description":"API - key сервиса dadata"
        },
    {
            "name": "MESSAGE_FOR_ORDER_ACTIVE",
            "type": "bool",
            "value": False,
            "description":"Включить Доп сообщение на экране заказа"
        },
    {
            "name": "MESSAGE_FOR_ORDER",
            "type": "text",
            "value": 'message in config',
            "description":"Доп сообщение на экране заказа"
        },
    {
        "name": "MESSAGE_FOR_ORDER_EDU_ACTIVE",
        "type": "bool",
        "value": False,
        "description": "Включить обучение"
    },
    {
        "name": "MESSAGE_FOR_ORDER_FIRST",
        "type": "text",
        "value": 'Обучалка до создания заказа в настройках',
        "description": "Обучалка до создания заказа"
    },
    {
        "name": "MESSAGE_FOR_ORDER_SECOND",
        "type": "text",
        "value": 'Диалог до создания заказа в настройках',
        "description": "Обучалка - Диалог до создания заказа"
    },
    {
                "name": "SMELL_PRICE",
                "type": "int",
                "value": 100,
                "description":"Стоимость удаления запаха м2"

            },
    {
                "name": "DIRT_PRICE",
                "type": "int",
                "value": 100,
                "description":"Стоимость сильно грязный"

            },
{
                "name": "COMB_OUT_PRICE",
                "type": "int",
                "value": 100,
                "description":"Стоимость доп вычеывания"

            },
{
                "name": "PERFUME_PRICE",
                "type": "int",
                "value": 100,
                "description":"Стоимость парфюма"

            },

]

