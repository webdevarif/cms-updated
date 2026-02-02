#!/bin/bash

# Digital Farmers CMS Production Status Check
# This script checks the status of all production services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_header() {
    echo -e "${BLUE}$1${NC}"
}

echo "🔍 Digital Farmers CMS Production Status Check"
echo "=========================================="

# Check nginx
log_header "🌐 NGINX Status"
if systemctl is-active --quiet nginx; then
    log_info "✅ Nginx is running"
    nginx_version=$(nginx -v 2>&1 | cut -d' ' -f3)
    echo "   Version: $nginx_version"
else
    log_error "❌ Nginx is not running"
fi

# Check nginx configuration
if nginx -t > /dev/null 2>&1; then
    log_info "✅ Nginx configuration is valid"
else
    log_error "❌ Nginx configuration has errors"
    nginx -t
fi

# Check gunicorn (systemd)
log_header "🦄 GUNICORN Status"
if systemctl is-active --quiet cms-gunicorn; then
    log_info "✅ Gunicorn (systemd) is running"
    systemctl status cms-gunicorn --no-pager -l
else
    log_warn "⚠️  Gunicorn (systemd) is not running"
fi

# Check background tasks (systemd)
log_header "⚙️  Background Tasks Status"
if systemctl is-active --quiet cms-background-tasks; then
    log_info "✅ Background tasks (systemd) are running"
    systemctl status cms-background-tasks --no-pager -l
else
    log_warn "⚠️  Background tasks (systemd) are not running"
fi

# Check supervisor processes
log_header "👥 SUPERVISOR Status"
if pgrep supervisord > /dev/null; then
    log_info "✅ Supervisor is running"
    supervisorctl status
else
    log_warn "⚠️  Supervisor is not running"
fi

# Check port 8000 (gunicorn)
log_header "🔌 Port 8000 Status"
if netstat -tlnp | grep -q ":8000 "; then
    log_info "✅ Port 8000 is listening"
    netstat -tlnp | grep ":8000 "
else
    log_error "❌ Port 8000 is not listening"
fi

# Check port 80/443 (nginx)
log_header "🔌 Web Server Ports"
if netstat -tlnp | grep -q ":80 "; then
    log_info "✅ Port 80 (HTTP) is listening"
else
    log_error "❌ Port 80 (HTTP) is not listening"
fi

if netstat -tlnp | grep -q ":443 "; then
    log_info "✅ Port 443 (HTTPS) is listening"
else
    log_warn "⚠️  Port 443 (HTTPS) is not listening (may be HTTP only)"
fi

# Check disk space
log_header "💾 Disk Space"
df -h /var/www /var/log

# Check memory usage
log_header "🧠 Memory Usage"
free -h

# Check recent logs
log_header "📋 Recent Logs"
echo "--- Gunicorn Error Log (last 10 lines) ---"
if [ -f /var/log/gunicorn/error.log ]; then
    tail -n 10 /var/log/gunicorn/error.log
else
    echo "No gunicorn error log found"
fi

echo ""
echo "--- Supervisor Log (last 5 lines) ---"
if [ -f /var/log/supervisor/supervisord.log ]; then
    tail -n 5 /var/log/supervisor/supervisord.log
else
    echo "No supervisor log found"
fi

# Check Django health
log_header "🏥 Django Health Check"
if curl -s http://localhost/health/ | grep -q "healthy"; then
    log_info "✅ Django health check passed"
else
    log_error "❌ Django health check failed"
fi

echo ""
log_info "Status check completed!"
echo ""
echo "🔧 Management Commands:"
echo "  - Restart nginx: systemctl restart nginx"
echo "  - Restart gunicorn: systemctl restart cms-gunicorn"
echo "  - Restart tasks: systemctl restart cms-background-tasks"
echo "  - View logs: tail -f /var/log/gunicorn/error.log"
echo "  - Supervisor: supervisorctl status"
