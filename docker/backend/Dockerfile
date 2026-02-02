FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY backend .

# Create necessary directories
RUN mkdir -p /app/media /app/staticfiles /app/logs

# Expose port
EXPOSE 8000

# Set default command for development
CMD ["sh", "-c", "python manage.py check && python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]
