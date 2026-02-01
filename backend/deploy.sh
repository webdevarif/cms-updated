#!/bin/bash

# Digital Farmers CMS Production Deployment Script
# This script sets up the production environment with nginx + gunicorn

set -e

echo "🚀 Digital Farmers CMS Production Deployment"
echo "=========================================="

# Configuration variables
PROJECT_DIR="/var/www/cms"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_DIR="$PROJECT_DIR/venv"
NGINX_CONF="/etc/nginx/sites-available/cms"
SYSTEMD_DIR="/etc/systemd/system"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root (use sudo)"
   exit 1
fi

# Create project directory structure
log_info "Creating project directory structure..."
mkdir -p $PROJECT_DIR/{backend,static,media,logs}
mkdir -p /var/log/{gunicorn,supervisor}
mkdir -p /var/run/{gunicorn,supervisor}

# Copy configuration files
log_info "Copying configuration files..."
cp gunicorn.conf.py $BACKEND_DIR/
cp nginx.conf $NGINX_CONF

# Set up permissions
log_info "Setting up permissions..."
chown -R www-data:www-data $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
chmod -R 777 /var/log/{gunicorn,supervisor}
chmod -R 777 /var/run/{gunicorn,supervisor}

# Install nginx if not present
if ! command -v nginx &> /dev/null; then
    log_info "Installing nginx..."
    apt-get update
    apt-get install -y nginx
fi

# Configure nginx
log_info "Configuring nginx..."
ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

# Install supervisor if not present
if ! command -v supervisord &> /dev/null; then
    log_info "Installing supervisor..."
    apt-get install -y supervisor
fi

# Copy supervisor configuration
log_info "Setting up supervisor..."
cp supervisor.conf /etc/supervisor/conf.d/cms.conf

# Set up systemd services (alternative to supervisor)
log_info "Setting up systemd services..."
cp cms-gunicorn.service $SYSTEMD_DIR/
cp cms-background-tasks.service $SYSTEMD_DIR/

# Reload systemd
systemctl daemon-reload

# Create startup scripts
log_info "Creating startup scripts..."

# Gunicorn startup script
cat > /usr/local/bin/start-cms-gunicorn << 'EOF'
#!/bin/bash
cd /var/www/cms/backend
source /var/www/cms/venv/bin/activate
gunicorn --config gunicorn.conf.py core.wsgi:application
EOF

chmod +x /usr/local/bin/start-cms-gunicorn

# Background tasks startup script
cat > /usr/local/bin/start-cms-tasks << 'EOF'
#!/bin/bash
cd /var/www/cms/backend
source /var/www/cms/venv/bin/activate
python manage.py process_tasks
EOF

chmod +x /usr/local/bin/start-cms-tasks

# Create log rotation
log_info "Setting up log rotation..."
cat > /etc/logrotate.d/cms << 'EOF'
/var/log/gunicorn/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        /bin/kill -USR1 `cat /var/run/gunicorn/cms_backend.pid 2> /dev/null` 2> /dev/null || true
    endscript
}

/var/log/supervisor/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF

# Display deployment summary
echo ""
echo "✅ Deployment setup complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Copy your Django project to: $BACKEND_DIR"
echo "2. Install Python dependencies: pip install -r requirements.txt"
echo "3. Run Django migrations: python manage.py migrate"
echo "4. Collect static files: python manage.py collectstatic"
echo "5. Set up environment variables in production settings"
echo "6. Choose your process manager:"
echo "   - Supervisor: supervisord -c /etc/supervisor/supervisord.conf"
echo "   - Systemd: systemctl start cms-gunicorn cms-background-tasks"
echo "7. Start nginx: systemctl start nginx"
echo "8. Enable services: systemctl enable nginx cms-gunicorn cms-background-tasks"
echo ""
echo "🔧 Configuration Files:"
echo "  - Gunicorn: $BACKEND_DIR/gunicorn.conf.py"
echo "  - Nginx: $NGINX_CONF"
echo "  - Supervisor: /etc/supervisor/conf.d/cms.conf"
echo "  - Systemd: $SYSTEMD_DIR/cms-*.service"
echo ""
echo "📁 Important Directories:"
echo "  - Project: $PROJECT_DIR"
echo "  - Logs: /var/log/gunicorn/, /var/log/supervisor/"
echo "  - PIDs: /var/run/gunicorn/, /var/run/supervisor/"
echo ""
log_info "Production nginx + gunicorn setup complete — ready for live server!"
