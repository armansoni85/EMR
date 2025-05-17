"""
WSGI config for emr project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
import environ
from django.core.wsgi import get_wsgi_application

# Initialize environ.Env with the path to .env file
env = environ.Env()

# Load environment variables from the .env file
environ.Env.read_env(".env")

# Access environment variables
ENV = env("ENV")


if ENV in ["production", "prod", "staging", "stag"]:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emr.prod_settings")
elif ENV in ["development"]:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emr.dev_settings")

application = get_wsgi_application()
