#!/usr/bin/env python
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")
django.setup()

from django.db import connection

# List of migrations to fake
migrations_to_fake = [
    ("ecommerce", "0001_initial"),
    ("entities", "0001_initial"),
    ("logs", "0001_initial"),
    ("mediafile", "0001_initial"),
    ("webhooks", "0001_initial"),
]

with connection.cursor() as cursor:
    for app, name in migrations_to_fake:
        try:
            cursor.execute(
                f"INSERT INTO django_migrations (app, name, applied) VALUES ('{app}', '{name}', '2026-01-28 20:07:00')"
            )
            print(f"{app} {name} migration faked")
        except Exception as e:
            print(f"Error faking {app} {name}: {e}")
