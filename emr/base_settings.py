import datetime
import logging
import os
import json
from django.utils.log import DEFAULT_LOGGING
import environ


env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")
ALLOWED_HOSTS = ["*"]
ENV = env("ENV")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django.contrib.gis",
    "drf_yasg",
    "rest_framework_simplejwt.token_blacklist",
    "rest_framework",
    "corsheaders",
    "django_filters",
    "ckeditor",
    "django_countries",
    # "django_celery_beat",
    # modules installed
    "user",
    "notification",
    "api_log",
    "hospital",
    "appointments",
    "employee",
    "consultation",
    "prescription",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",  # for user agent
    # "api_log.custom_middleware.UserLogHistory",  # for logging request
]

ROOT_URLCONF = "emr.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "emr.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
        "CONN_MAX_AGE": 3600,
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_ROOT = os.path.join(
    BASE_DIR, "assets"
)  # it will collect all static files from project into assets folder
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]  # we need to extra path on which django should look for static file except static_root folder,cons: user static and system static will be separate


FILE_UPLOAD_HANDLERS = ["django.core.files.uploadhandler.TemporaryFileUploadHandler"]
# Media files (Uploaded by users)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "emr.authenticate.CustomAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
    "EXCEPTION_HANDLER": "emr.handle_exceptions.custom_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "20/min",
        "user": "100/min",
        "on_boarding": "50/min",
        "login": "3/min",
        "image_upload": "20/min",
        "OTP": "10/min",
    },
    "DEFAULT_PAGINATION_CLASS": "base.utils.CustomLimitOffsetPagination",
    "PAGE_SIZE": 10,
}


CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = []

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# user model
AUTH_USER_MODEL = "user.CustomUser"


# Celery settings
COMMON_CELERY_BROKER_URL = env("COMMON_CELERY_BROKER_URL")
COMMON_CELERY_TASK_DEFAULT_QUEUE = env("COMMON_CELERY_TASK_DEFAULT_QUEUE")


# this is for logs in console
API_URL = env("API_URL")
logging
LOGGING_CONFIG = None
LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s - %(module)s.%(funcName)s - %(name)s - %(levelname)s - %(message)s - %(exc_text)s",
            },
            "django.server": DEFAULT_LOGGING["formatters"]["django.server"],
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "django.server": DEFAULT_LOGGING["handlers"]["django.server"],
        },
        "loggers": {
            "": {
                "level": LOGLEVEL,
                "handlers": ["console"],
            },
            "django.db.backends": {
                "level": LOGLEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            # Default runserver request logging
            "django.server": DEFAULT_LOGGING["loggers"]["django.server"],
        },
    }
)

# this is for logs will be in file.
# API_URL = env('API_URL')
# # logging
# LOGGING_CONFIG = None
# # LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()

# DB_QUERY_LOG_FILE = "db_queries.log"  # Change this path to your desired log file location

# LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()

# # Configure logging for Django database queries
# logging.config.dictConfig(
#     {
#         "version": 1,
#         "disable_existing_loggers": False,
#         "formatters": {
#             "db_queries": {
#                 "format": "%(asctime)s - %(message)s",
#             },
#         },
#         "handlers": {
#             "db_queries_file": {
#                 "class": "logging.FileHandler",
#                 "filename": DB_QUERY_LOG_FILE,
#                 "formatter": "db_queries",
#             },
#         },
#         "loggers": {
#             "django.db.backends": {
#                 "level": "DEBUG",  # Adjust log level as needed (DEBUG, INFO, etc.)
#                 "handlers": ["db_queries_file"],
#                 "propagate": False,
#             },
#         },
#         "root": {
#             "level": LOGLEVEL,
#             "handlers": ["db_queries_file"],
#         },
#     }
# )


SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        }
    },
}

# LOGIN_URL = str(env("ADMIN_PANEL_URL"))
FILE_UPLOAD_PERMISSIONS = 0o644

MAX_RETRY_LIMIT = int(env("MAX_RETRY_LIMIT"))  # since its coming in str
# API_URL = env("API_URL")


# Caching UserAgent
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
#         "LOCATION": "127.0.0.1:11211",
#     }
# }
USER_AGENTS_CACHE = "default"

# LOGIN BLOCK CONFIG
# LOGIN_ATTEMPTS_ALLOWED_RETRY_NUMBER = int(env("LOGIN_ATTEMPTS_ALLOWED_RETRY_NUMBER"))
# LOGIN_BLOCK_TEMPORARY_FOR_X_HOUR = int(env("LOGIN_BLOCK_TEMPORARY_FOR_X_HOUR"))
# LOGIN_BLOCK_ADMIN = env("LOGIN_BLOCK_ADMIN")
# Notification to be deleted config
# NOTIFICATION_TO_BE_DELETED_AFTER_X_DAYS = int(
#     env("NOTIFICATION_TO_BE_DELETED_AFTER_X_DAYS")
# )
# PUSH_NOTIFICATION_BATCH_SIZE = int(env("PUSH_NOTIFICATION_BATCH_SIZE"))


# Reset Password OTP Expiry Days
# RESET_PASSWORD_OTP_EXPIRY_IN_DAYS = int(env("RESET_PASSWORD_OTP_EXPIRY_IN_DAYS"))
RESET_PASSWORD_OTP_EXPIRY_IN_MINS = int(env("RESET_PASSWORD_OTP_EXPIRY_IN_MINS"))


# # Max Transaction Sequence Number
# MAX_TRANSACTION_SEQUENCE_NUMBER = int(env("MAX_TRANSACTION_SEQUENCE_NUMBER"))

# DEFAULT_CURRENCY_CODE = str(env("DEFAULT_CURRENCY_CODE"))
ADMIN_PANEL_URL = env("ADMIN_PANEL_URL")
LOGIN_THROTTLE_RATE = str(env("LOGIN_THROTTLE_RATE"))
DEBUG_ADMIN_PANEL = True if env("DEBUG_ADMIN_PANEL").lower() == "true" else False
# SECURITY_ADMIN = env("SECURITY_ADMIN")


# DEFAULT_FILE_STORAGE = "base.utils.CustomS3Boto3Storage"
# STATICFILES_STORAGE = "base.utils.StaticS3Boto3Storage"

# AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
# AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
# AWS_STATIC_STORAGE_BUCKET_NAME = env("AWS_STATIC_STORAGE_BUCKET_NAME")
# AWS_DEFAULT_REGION = env("AWS_DEFAULT_REGION")

# AWS_DEFAULT_ACL = None
# AWS_BUCKET_ACL = None

# AWS_S3_BASE_URL = f"https://{AWS_STORAGE_BUCKET_NAME.lower()}.s3.amazonaws.com"


# E-mail
# SES
# EMAIL_BACKEND = "django_amazon_ses.EmailBackend"
# DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
# EMAIL_FROM_NAME = env("EMAIL_FROM_NAME")

# Gmail Email Service
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# FRONTEND URL
FRONTEND_URL = env("FRONTEND_URL")
API_URL = env("API_URL")

# ChatGPT
OPENAI_API_KEY = env("OPENAI_API_KEY")
