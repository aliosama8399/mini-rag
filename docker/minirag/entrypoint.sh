#! /bin/bash
set -e
echo "Running Database Migrations"
cd /app/models/db_schemes/minirag/
alembic upgrade head || { echo "Alembic migration failed"; exit 1; }
echo "Alembic migration finished"
cd /app
exec "$@"
