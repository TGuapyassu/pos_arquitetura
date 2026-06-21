#!/bin/sh
set -e

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  echo "Executando migrations (alembic upgrade head)..."
  alembic upgrade head
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
