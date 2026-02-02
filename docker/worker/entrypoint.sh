#!/bin/bash
set -e

echo "Starting Celery worker..."

exec celery -A core worker -l info
