"""
ASGI config for emr project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
import environ
from django.core.asgi import get_asgi_application


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

application = get_asgi_application()
