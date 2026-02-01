# Production Deployment Guide

This guide covers setting up Digital Farmers CMS in production using nginx + gunicorn.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx (80/443) │───▶│ Gunicorn (8000) │───▶│ Django App      │
│                 │    │                 │    │                 │
│ • SSL/TLS       │    │ • 4 Workers      │    │ • Background     │
│ • Static Files  │    │ • 2 Threads      │    │   Tasks          │
│ • Media Files   │    │ • Process Mgmt   │    │ • Database       │
│ • Rate Limiting │    │ • Health Checks  │    │ • Cache          │
│ • Security      │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Ubuntu 20.04+ or CentOS 8+
- Python 3.8+
- Nginx
- PostgreSQL (recommended)
- Redis (for caching/background tasks)

## 🚀 Quick Deployment

### 1. Run the Deployment Script

```bash
sudo bash deploy.sh
```

This script will:
- Create directory structure
- Set up permissions
- Install nginx and supervisor
- Copy configuration files
- Set up log rotation
- Create systemd services

### 2. Deploy Your Application

```bash
# Copy your Django project
sudo cp -r /path/to/your/cms/* /var/www/cms/backend/

# Install dependencies
cd /var/www/cms/backend
sudo -u www-data /var/www/cms/venv/bin/pip install -r requirements.txt

# Run migrations
sudo -u www-data /var/www/cms/venv/bin/python manage.py migrate

# Collect static files
sudo -u www-data /var/www/cms/venv/bin/python manage.py collectstatic --noinput

# Create superuser (if needed)
sudo -u www-data /var/www/cms/venv/bin/python manage.py createsuperuser
```

### 3. Configure Environment

Edit `/var/www/cms/backend/core/settings/production.py`:

```python
# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "cms_production",
        "USER": "cms_user",
        "PASSWORD": "secure_password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# Security
SECRET_KEY = "your-very-secret-key-here"
DEBUG = False
ALLOWED_HOSTS = ["your-domain.com", "www.your-domain.com"]

# SSL
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 4. Start Services

#### Option A: Systemd (Recommended)

```bash
# Start services
sudo systemctl start cms-gunicorn cms-background-tasks nginx

# Enable on boot
sudo systemctl enable cms-gunicorn cms-background-tasks nginx

# Check status
sudo systemctl status cms-gunicorn cms-background-tasks nginx
```

#### Option B: Supervisor

```bash
# Start supervisor
sudo supervisord -c /etc/supervisor/supervisord.conf

# Check status
sudo supervisorctl status

# Start processes
sudo supervisorctl start cms_gunicorn cms_background_tasks
```

## 📁 Configuration Files

### Gunicorn (`gunicorn.conf.py`)

```python
# Server socket
bind = "0.0.0.0:8000"

# Worker processes
workers = 4
worker_class = "gthread"
threads = 2

# Timeout
timeout = 30
keepalive = 10

# Logging
loglevel = "info"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"

# Environment
raw_env = [
    "DJANGO_SETTINGS_MODULE=core.settings.production",
    "PYTHONPATH=/var/www/cms/backend",
]
```

### Nginx (`nginx.conf`)

```nginx
# Upstream backend
upstream cms_backend {
    server 0.0.0.0:8000;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static/ {
        alias /var/www/cms/static/;
        expires 1y;
    }

    # Media files
    location /media/ {
        alias /var/www/cms/media/;
        expires 30d;
    }

    # Django application
    location / {
        proxy_pass http://cms_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔧 Management Commands

### Service Management

```bash
# Systemd
sudo systemctl start|stop|restart|status cms-gunicorn
sudo systemctl start|stop|restart|status cms-background-tasks
sudo systemctl start|stop|restart|status nginx

# Supervisor
sudo supervisorctl start|stop|restart cms_gunicorn
sudo supervisorctl start|stop|restart cms_background_tasks
sudo supervisorctl status
```

### Log Management

```bash
# View logs
sudo tail -f /var/log/gunicorn/error.log
sudo tail -f /var/log/gunicorn/access.log
sudo tail -f /var/log/supervisor/supervisord.log

# Rotate logs
sudo logrotate -f /etc/logrotate.d/cms
```

### Django Management

```bash
cd /var/www/cms/backend
sudo -u www-data /var/www/cms/venv/bin/python manage.py <command>

# Common commands
manage.py migrate
manage.py collectstatic
manage.py createsuperuser
manage.py shell
manage.py check --deploy
```

## 🔍 Monitoring and Health Checks

### Status Check Script

```bash
sudo bash status.sh
```

This script checks:
- Nginx status and configuration
- Gunicorn processes
- Background task processors
- Port availability
- Disk space and memory
- Django health endpoint

### Health Endpoints

- `/health/` - Basic health check
- `/admin/` - Django admin (monitor background tasks)
- `/api/v2/health/` - API health check

## 🔒 Security Considerations

### SSL/TLS Setup

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Firewall Setup

```bash
# UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# iptables (alternative)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

### Database Security

```bash
# Create database user
sudo -u postgres createuser cms_user
sudo -u postgres createdb cms_production
sudo -u postgres psql -c "ALTER USER cms_user PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE cms_production TO cms_user;"
```

## 📈 Performance Optimization

### Gunicorn Tuning

```python
# Adjust workers based on CPU cores
workers = (2 * CPU_CORES) + 1

# For I/O bound applications
worker_class = "gevent"
workers = CPU_CORES * 4

# For CPU bound applications
worker_class = "sync"
workers = CPU_CORES + 1
```

### Nginx Caching

```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Database Optimization

```python
# In production.py
DATABASES["default"]["OPTIONS"] = {
    "MAX_CONNS": 20,
    "CONN_MAX_AGE": 600,
}
```

## 🚨 Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   - Check if gunicorn is running
   - Verify nginx configuration
   - Check port 8000 availability

2. **Static files not loading**
   - Run `collectstatic`
   - Check file permissions
   - Verify nginx static file configuration

3. **Database connection errors**
   - Check database credentials
   - Verify database is running
   - Check firewall rules

4. **Background tasks not running**
   - Check process_tasks service
   - Verify background_task tables exist
   - Check logs for errors

### Debug Commands

```bash
# Test nginx configuration
sudo nginx -t

# Test gunicorn directly
curl http://localhost:8000/

# Check systemd logs
sudo journalctl -u cms-gunicorn -f

# Check supervisor logs
sudo supervisorctl tail cms_gunicorn

# Django debug
python manage.py check --deploy
```

## 🔄 Backup Strategy

### Database Backup

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/var/backups/cms"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump cms_production > "$BACKUP_DIR/cms_backup_$DATE.sql"
```

### File Backup

```bash
# Backup static files
rsync -av /var/www/cms/static/ /backup/cms/static/

# Backup media files
rsync -av /var/www/cms/media/ /backup/cms/media/
```

## 📞 Support

For issues with this deployment setup:

1. Check the status script output
2. Review log files
3. Verify configuration files
4. Test individual components

---

**✅ Production nginx + gunicorn setup complete — ready for live server!**
