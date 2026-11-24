# Backend Dockerfile for Emirates Baggage360
FROM python:3.11-slim

# Install system dependencies for psycopg
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency manifests
COPY pyproject.toml ./

# Copy application code (needed for pip install . to work)
COPY app/ ./app/

# Install dependencies (default is base dependencies, can be overridden with INSTALL_SPEC)
ARG INSTALL_SPEC=.
RUN pip install --no-cache-dir "$INSTALL_SPEC"
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Copy entrypoint script
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Expose backend port
EXPOSE 9000
# x-preview-port marker for preview environment
# x-preview-port: 9000

# Run migrations and seed on startup, then start the server
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]
