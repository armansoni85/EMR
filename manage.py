#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import environ

# Initialize environ.Env with the path to .env file
env = environ.Env()

# Load environment variables from the .env file
environ.Env.read_env(".env")

# Access environment variables
ENV = env("ENV")


def main():
    """Run administrative tasks."""

    if ENV in ["production", "prod", "staging", "stag"]:
        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE", "emr.prod_settings"
        )
    elif ENV in ["development"]:
        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE", "emr.dev_settings"
        )

    sys.stdout.write("\033[33m ................ \033[0m \n")
    sys.stdout.write("\033[33m ................ \033[0m \n")
    sys.stdout.write(
        "\033[91m \033[1m Please make super admin during initial setup \033[0m \n"
    )
    sys.stdout.write("\033[33m ................ \033[0m \n")
    sys.stdout.write("\033[33m ................ \033[0m \n") 

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
