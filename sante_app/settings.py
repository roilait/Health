# Configure Django App for Heroku.
import sys
# To install heroku in django the command line django-heroku changed to: pip install django-on-heroku
import django_on_heroku
import os
import dj_database_url
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from decouple import config # pip install python-decouple

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIRS = os.path.join(BASE_DIR, "templates")
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
# Sender email parameters
E_MAIL_HOST_USER = config("EMAIL_HOST_USER")
E_MAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
E_MAIL_HOST = config("EMAIL_HOST", default='localhost')
E_MAIL_PORT = config("EMAIL_PORT", default=25, cast=int)
# Database configuration
DB_NAME = config("DB_NAME")
DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD")
DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT", default=5432, cast=int)
# Allowed hosts
ALLOWED_HOSTS = config("ALLOWED_HOSTS")

DJANGORESIZED_DEFAULT_SIZE = [800, 600]
# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    ""'django.contrib.auth',
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # My apps
    "app",
    "crispy_forms",
    #"bootstrap4",
    "crispy_bootstrap5",  # Forgetting this was probably your error
    "bootstrap_datepicker_plus",
    "phonenumber_field",
    # 'captcha',
    # 'djcelery',
]

AUTH_USER_MODEL = "app.Members"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sante_app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Adding the TEMPLATES_DIRS here
        "DIRS": [TEMPLATES_DIRS],
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

WSGI_APPLICATION = "sante_app.wsgi.application"
# Database
# https://simpleisbetterthancomplex.com/2015/11/26/package-of-the-week-python-decouple.html
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': BASE_DIR / 'db.sqlite3',
    }
}

db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES["default"].update(db_from_env)

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {  # Checks if password is similar to user name or other attributes
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {  # Checks for min length
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        # We can pass options to modify behaviour
        # 'OPTION': {'min_length':9},
    },
    {  # checks for weak password
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {  # Make sure password has numbers
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
TEMPLATED_EMAIL_BACKEND = "templated_email.backends.vanilla_django.TemplateBackend"

# Broker Settings
CELERY_BROKER_URL = "redis://:p866b6496b58bc1737d15d6470ed5f65016fe13a03c5d2753e1ab5246d5deee1f@ec2-54-164-74-91.compute-1.amazonaws.com:21260"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

# Email information
EMAIL_HOST = E_MAIL_HOST
EMAIL_PORT = E_MAIL_PORT
EMAIL_HOST_USER = E_MAIL_HOST_USER
EMAIL_HOST_PASSWORD = E_MAIL_HOST_PASSWORD
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True

# celery==4.3.0
# celery -A gp_project worker -l info
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIAFILES_DIRS = (os.path.join(BASE_DIR, "media"),)

# CRISPY_TEMPLATE_PACK = "bootstrap4"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

BOOTSTRAP4 = {
    "include_jquery": True,
}

django_on_heroku.settings(locals())
