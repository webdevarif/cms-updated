# Gunicorn configuration for Digital Farmers CMS
# Production-ready configuration with optimal worker/thread settings

import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
worker_connections = 1000
threads = 2  # Only used with gthread worker class

# Restart workers after this many requests, this can help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Timeout for handling requests
timeout = 30
keepalive = 10

# Logging
loglevel = "info"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'cms_backend'

# Server mechanics
daemon = False
pidfile = '/var/run/gunicorn/cms_backend.pid'
user = 'www-data'
group = 'www-data'
tmp_upload_dir = None

# SSL (if needed - usually handled by nginx)
keyfile = None
certfile = None

# Application
wsgi_module = "core.wsgi:application"
pythonpath = '/var/www/cms/backend'

# Worker timeout
graceful_timeout = 30

# Preload application code
preload_app = True

# Additional settings for production
worker_tmp_dir = "/dev/shm"

# Environment variables
raw_env = [
    "DJANGO_SETTINGS_MODULE=core.settings.production",
    "PYTHONPATH=/var/www/cms/backend",
]

# Function to set environment variables dynamically
def on_starting(server):
    """Called just before the master process is initialized."""
    # Set production environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.production')
    os.environ.setdefault('PYTHONPATH', '/var/www/cms/backend')

    # Ensure production settings are used
    if os.getenv('DJANGO_DEBUG', 'False') == 'True':
        print("WARNING: DEBUG mode is enabled in production!")

def on_reload(server):
    """Called when the server is reloaded."""
    print("Gunicorn server reloaded")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    import django
    django.setup()

def pre_fork(server, worker):
    """Called just prior to forking the worker subprocess."""
    pass

def pre_exec(server):
    """Called just prior to exec'ing off the master process."""
    pass

def when_ready(server):
    """Called when the server is ready to receive connections."""
    print(f"Gunicorn server ready with {workers} workers on {bind}")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    print(f"Worker {worker.pid} received SIGABRT")

def worker_int(worker):
    """Called when a worker received the SIGINT or SIGQUIT signal."""
    print(f"Worker {worker.pid} received SIGINT/SIGQUIT")

# Health check
def application():
    """Application factory for gunicorn."""
    from core.wsgi import application as app
    return app
