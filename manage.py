#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks."""
import os
import sys
import django
# https://www.codementor.io/@garethdwyer/creating-and-hosting-a-basic-web-application-with-django-with-repl-it-lohsyub20


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sante_app.settings')
    django.setup()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()