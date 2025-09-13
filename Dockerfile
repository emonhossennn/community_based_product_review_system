FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE myproject.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY myproject/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Add faker to requirements
RUN pip install faker

# Copy project
COPY myproject/ /app/

# Collect static files
RUN python manage.py collectstatic --noinput --clear

# Create entrypoint script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Expose port
EXPOSE 8000

# Run the application
CMD ["./docker-entrypoint.sh"]
