#!/bin/sh
# Backend entrypoint: run migrations and seed, then start the server
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Seeding database..."
python -m app.seed

echo "Starting backend server..."
exec "$@"
