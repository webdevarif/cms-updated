#!/usr/bin/env python
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute(
        "INSERT INTO django_migrations (app, name, applied) VALUES ('mediafile', '0001_initial', '2026-01-28 20:07:00')"
    )
    print("Mediafile migration faked")
