import os
import environ
from celery import Celery

# Initialize environ.Env with the path to your .env file
env = environ.Env()

# Load environment variables from the .env file
environ.Env.read_env(".env")

# Access your environment variables
ENV = env("ENV")

if ENV in ["production", "prod", "staging", "stag"]:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emr.prod_settings")
elif ENV in ["development"]:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emr.dev_settings")

common_app = Celery("emr_common")
common_app.config_from_object(
    "django.conf:settings", force=True, namespace="COMMON_CELERY"
)

common_app.autodiscover_tasks(
    [
        "user",
        "company",
        "merchant",
        "sites",
        "masterdata",
        "brand",
        "vendornetwork",
        "fuel",
        "program",
        "contract",
        "fleet",
        "subaccount",
        "vehicle",
        "terminal",
        "identification",
        "rule",
        "transaction",
        "billing",
        "notification",
        "dispersion",
    ]
)
