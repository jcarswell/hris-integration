"""
Django settings for HRIS Integration project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = Path(str(BASE_DIR) + '\\logs\\')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4twwe^$qr=ee$(sy_eyc&1*w_1ubk!+^6z(&l&9-ftqd+5-3ja'
ENCRYPTION_KEY = 'jj5XwwAsmLIKU1ET_sdft7yBrfaAWhCcaW61BqUQfvE='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hirs_admin',
    'cron',
    'ftp_import',
    'ad_export',
    'corepoint_export',
    'smtp_client'
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

ROOT_URLCONF = 'hris_integration.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hris_integration.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'HrisIntegration',
        'HOST': 'LOCALHOST',
        'OPTIONS': {
            'driver': "SQL Server Native Client 11.0"
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Regina'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - [%(levelname)s] - (%(name)s-%(process)d:%(thread)d) - %(message)s'
        },
        'simple': {
            'format': '%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': os.getenv('DJANGO_LOG_LEVEL','DEBUG' if DEBUG else 'INFO'),
            'class': 'logging.StreamHandler',
            'formatter': 'simple' if not DEBUG else 'verbose'
        },
        'log': {
            'level': os.getenv('DJANGO_LOG_LEVEL','DEBUG' if DEBUG else 'INFO'),
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR) + '\\system.log',
            'maxBytes': 10240000,
            'backupCount': 10,
            'formatter': 'simple' if not DEBUG else 'verbose'
        }
    },
    'root': {
        'handlers': ['console','log'],
        'level': os.getenv('DJANGO_LOG_LEVEL','DEBUG' if DEBUG else 'INFO'),
    },
    'loggers': {
        'default': {
            'handlers': ['console','log'],
            'propagate': True,
        }
    }
}