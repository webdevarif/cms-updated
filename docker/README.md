# Digital Farmers CMS - Docker Setup

This directory contains all Docker-related files for running the Digital Farmers CMS application.

## Quick Start

### Development Environment

```bash
# Start development stack
docker compose -f docker/docker-compose.yml up --build

# Start in detached mode
docker compose -f docker/docker-compose.yml up -d

# View logs
docker compose -f docker/docker-compose.yml logs -f
```

### Production Environment

```bash
# Start production stack
docker compose -f docker/docker-compose.prod.yml up --build -d

# Scale workers if needed
docker compose -f docker/docker-compose.prod.yml up -d --scale worker=3

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

## Services

### Backend
- **Image**: Built from `docker/backend/Dockerfile`
- **Port**: 8000
- **Environment**: Configurable via `docker/env/backend.env`
- **Development**: Uses Django development server with live reload
- **Production**: Uses Gunicorn with optimized settings

### Database
- **Image**: PostgreSQL 15-alpine
- **Port**: 5432
- **Environment**: Configured via `docker/env/db.env`
- **Persistence**: Named volume for data

### Redis
- **Image**: Redis 7-alpine
- **Port**: 6379
- **Persistence**: Named volume for data

### Worker
- **Image**: Built from `docker/worker/Dockerfile`
- **Purpose**: Celery background tasks
- **Environment**: Same as backend, connects to Redis

### Nginx
- **Image**: nginx:1.25-alpine
- **Ports**: 80, 443
- **Purpose**: Reverse proxy, static file serving
- **Configuration**: Uses `docker/nginx/nginx.conf`

## Environment Files

### Required Environment Variables

#### `docker/env/backend.env.example`
```bash
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
DJANGO_SETTINGS_MODULE=core.settings.development
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://redis:6379/0
REDIS_CACHE_URL=redis://redis:6379/1
```

#### `docker/env/db.env.example`
```bash
POSTGRES_DB=cms_db
POSTGRES_USER=cms_user
POSTGRES_PASSWORD=your-db-password-here-change-in-production
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql://cms_user:your-db-password-here@db:5432/cms_db
```

#### `docker/env/redis.env.example`
```bash
REDIS_URL=redis://redis:6379/0
REDIS_CACHE_URL=redis://redis:6379/1
```

## Management Commands

### Database Operations
```bash
# Create superuser
docker compose -f docker/docker-compose.yml exec backend python manage.py createsuperuser

# Run migrations
docker compose -f docker/docker-compose.yml exec backend python manage.py migrate

# Collect static files
docker compose -f docker/docker-compose.yml exec backend python manage.py collectstatic

# Django shell
docker compose -f docker/docker-compose.yml exec backend python manage.py shell
```

### Worker Operations
```bash
# View worker logs
docker compose -f docker/docker-compose.yml logs worker

# Check active tasks
docker compose -f docker/docker-compose.yml exec backend python manage.py celery inspect active
```

### Production Specific
```bash
# Scale workers
docker compose -f docker/docker-compose.prod.yml up -d --scale worker=3

# Reload configuration (if needed)
docker compose -f docker/docker-compose.prod.yml restart
```

## Development Tips

- **Live Reload**: Backend code is mounted as a volume, so changes are reflected immediately
- **Database**: Uses PostgreSQL in Docker for consistency with production
- **Static Files**: Collected at startup, but can be collected manually with `collectstatic`
- **Environment Variables**: Copy `.example` files to `.env` and customize as needed

## Production Tips

- **Security**: Use strong secrets and change default passwords
- **Performance**: Adjust worker count based on load
- **Monitoring**: Consider adding health checks and monitoring tools
- **Backups**: Ensure database volumes are properly backed up
- **Updates**: Use rolling updates for zero-downtime deployments
