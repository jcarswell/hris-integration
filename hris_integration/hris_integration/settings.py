# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Core settings model. Do not edit this file directly. instead, edit the
config.py file that is generated when you run the setup script.
"""

import os
import sys

if sys.version_info.major < 3 and sys.version_info.minor < 8:
    raise RuntimeError("Python 3.8 or higher is required to run this application.")

from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = Path(BASE_DIR, "logs")
VERSION = "0.3.1"

if os.getenv("CONFIG_PATH"):
    sys.path.append(os.getenv("CONFIG_PATH"))
    try:
        import config
    except ImportError:
        try:
            from . import config
        except ImportError:
            raise ImproperlyConfigured(
                "Unable to import config.py. Please run the setup script."
            )
else:
    try:
        from . import config
    except ImportError:
        raise ImproperlyConfigured(
            "Unable to import config.py. Please run the setup script."
        )

for key in ["ALLOWED_HOSTS", "DATABASE", "SECRET_KEY", "ENCRYPTION_KEY"]:
    if not hasattr(config, key) and getattr(config, key):
        raise ImproperlyConfigured(f"Missing required config key: {key}")

DATABASES = {"default": None}
DATABASES["default"] = getattr(config, "DATABASE", {})
SECRET_KEY = getattr(config, "SECRET_KEY", None)
ENCRYPTION_KEY = getattr(config, "ENCRYPTION_KEY", None)
DEBUG = getattr(config, "DEBUG", False)
ALLOWED_HOSTS = getattr(config, "ALLOWED_HOSTS", [])
TIME_ZONE = getattr(config, "TIME_ZONE", "UTC")
STATIC_ROOT = getattr(config, "STATIC_ROOT", None)
STATIC_URL = getattr(config, "STATIC_URL", None)
MEDIA_ROOT = getattr(config, "MEDIA_ROOT", None)
PASSWORD_LENGTH = getattr(config, "PASSWORD_LENGTH", 12)
PASSWORD_CHARS = getattr(config, "PASSWORD_CHARS", "abcdefABCDEF1234567890!@#$%^&*()")
ADMINS = getattr(config, "ADMINS", [])
USE_I18N = getattr(config, "USE_I18N", True)
USE_L10N = getattr(config, "USE_L10N", True)
USE_TZ = getattr(config, "USE_TZ", True)

MEDIA_URL = "media/"  # DO NOT CHANGE THIS IT IS HARD CODED IN THE APP

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "mptt",
    "settings",
    "hirs_admin",
    "active_directory",
    "extras",
    "cron",
    "ftp_import",
    "ad_export",
    "smtp_client",
    "organization",
    "employee",
    "user_applications",
    "drf_yasg",
]
if hasattr(config, "ADDITIONAL_APPS"):
    INSTALLED_APPS += config.ADDITIONAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if hasattr(config, "ADDITIONAL_MIDDLEWARE"):
    MIDDLEWARE += config.ADDITIONAL_MIDDLEWARE

ROOT_URLCONF = "hris_integration.urls"

STATICFILES_DIRS = [
    Path(BASE_DIR, "static-core", "js"),
    Path(BASE_DIR, "static-core", "css"),
    Path(BASE_DIR, "static-core", "img"),
    ("docs", Path(BASE_DIR, "static-core", "docs")),
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [Path(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
            ],
        },
    },
]

WSGI_APPLICATION = "hris_integration.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"]
}

# Internationalization
LANGUAGE_CODE = "en-us"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(asctime)s - (%(name)s) - [%(levelname)s] %(message)s"},
        "simple": {
            "format": "%(asctime)s - [%(levelname)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": os.getenv("DJANGO_LOG_LEVEL", "DEBUG" if DEBUG else "INFO"),
            "class": "logging.StreamHandler",
            "formatter": "simple" if not DEBUG else "verbose",
        },
        "log": {
            "level": os.getenv("DJANGO_LOG_LEVEL", "DEBUG" if DEBUG else "INFO"),
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR) + "\\system.log",
            "maxBytes": 10240000,
            "backupCount": 10,
            "formatter": "simple" if not DEBUG else "verbose",
        },
    },
    "root": {
        "handlers": ["console", "log"],
        "level": os.getenv("DJANGO_LOG_LEVEL", "DEBUG" if DEBUG else "INFO"),
    },
    "loggers": {
        "default": {
            "handlers": ["console", "log"],
            "propagate": True,
        }
    },
}
