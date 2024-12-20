import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _
from environs import Env
from puput import PUPUT_APPS

env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG", default=False)
DEPLOYED = env.bool("DEPLOYED", default=True)
LOCAL_DEVELOPMENT = env.bool("LOCAL_DEVELOPMENT", default=False)

ALLOWED_HOSTS = ["igorsimb.ru", "www.igorsimb.ru", "localhost", "127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third-party
    "django_extensions",
    "debug_toolbar",
    "allauth",
    "allauth.account",
    "widget_tweaks",
    "mathfilters",
    "django_quill",
    "crispy_forms",
    "crispy_bootstrap5",
    "rangefilter",
    # Local
    "blog",
    "core.apps.CoreConfig",
    "accounts.apps.AccountsConfig",
    "store",
    "store_users",
]
INSTALLED_APPS += PUPUT_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "igorsimb.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "accounts", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "igorsimb.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if LOCAL_DEVELOPMENT:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": "u1853808_default",
            "USER": "u1853808_default",
            "PASSWORD": "NhJxp160xyJ5DYhR",
            "HOST": "localhost",
        }
    }


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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", _("English")),
    ("ru", _("Russian")),
]

TIME_ZONE = "Europe/Moscow"

USE_I18N = True
# WAGTAIL_I18N_ENABLED = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (BASE_DIR / "locale/",)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

# STATIC_URL = '/static/'
# STATICFILES_DIRS = BASE_DIR / 'static',
# STATIC_ROOT = BASE_DIR / 'staticfiles'

if LOCAL_DEVELOPMENT:
    STATICFILES_DIRS = [BASE_DIR / "static"]
else:
    STATIC_ROOT = "static/"

STATIC_DIR = [BASE_DIR / "static"]
STATIC_URL = "/static/"

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.CustomUser"

# django-debug-toolbar
INTERNAL_IPS = [
    "127.0.0.1",
]

# django-allauth config
SITE_ID = 1
LOGIN_REDIRECT_URL = "core:main"
ACCOUNT_LOGOUT_REDIRECT = "core:main"
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
SERVER_EMAIL = env("SERVER_EMAIL")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

ACCOUNT_SESSION_REMEMBER = None  # True/False/None; None = ask user
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True

# Translation
LOCALE_PATHS = (BASE_DIR / "locale/",)


# Crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Quill
QUILL_CONFIGS = {
    "default": {
        "theme": "snow",
        "modules": {
            "syntax": True,
            "toolbar": [
                [
                    {"font": []},
                    {"header": []},
                    {"align": []},
                    "bold",
                    "italic",
                    "underline",
                    "strike",
                    "blockquote",
                    {"color": []},
                    {"background": []},
                ],
                ["code-block", "link"],
                ["clean"],
            ],
        },
    }
}

# WAGTAIL / PUPUT settings
# This is the human-readable name of your Wagtail install
# which welcomes users upon login to the Wagtail admin.
WAGTAIL_SITE_NAME = "Igorsimb Blog"
WAGTAILADMIN_BASE_URL = "http://localhost:8000/" if LOCAL_DEVELOPMENT else "igorsimb.ru"

# Language detection settings
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365  # One year
LANGUAGE_COOKIE_SECURE = not DEBUG

# Additional language settings
USE_ACCEPT_LANGUAGE_HEADER = True  # Enable browser language detection when no django_language cookie is set.
ACCEPT_LANGUAGE_HEADER = 'HTTP_ACCEPT_LANGUAGE'
