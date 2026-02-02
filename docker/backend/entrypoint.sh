#!/bin/bash
set -e

echo "Starting Django application..."

# Collect static files if in production
if [ "$DJANGO_SETTINGS_MODULE" = "core.settings.production" ]; then
    python manage.py collectstatic --noinput --clear || echo "Collectstatic failed"
fi

# Run migrations if needed
if [ "$RUN_MIGRATIONS" = "true" ]; then
    python manage.py migrate --noinput || echo "Migration failed"
fi

# Start the application
if [ "$DJANGO_SETTINGS_MODULE" = "core.settings.production" ]; then
    echo "Starting with Gunicorn..."
    exec gunicorn --config gunicorn.conf.py core.wsgi:application
else
    echo "Starting with Django development server..."
    exec python manage.py runserver 0.0.0.0:8000
fi
