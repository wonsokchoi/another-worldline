#!/bin/bash
# Run Alembic migrations for Another Worldline backend
# Usage: ./migrate.sh

set -e

BACKEND_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BACKEND_DIR"

# Add PostgreSQL 16 to PATH
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"

echo "=== Another Worldline DB Migration ==="
echo "Backend dir: $BACKEND_DIR"

# Check .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "Please update .env with correct values."
fi

# Load .env
export $(grep -v '^#' .env | xargs)
echo "DATABASE_URL: $DATABASE_URL"

# Run migration via poetry
echo ""
echo "Running: alembic upgrade head"
poetry run alembic upgrade head

echo ""
echo "=== Migration complete! ==="

# Verify tables
echo ""
echo "=== Verifying tables ==="
DB_NAME="another_worldline"
psql -d "$DB_NAME" -c "\dt" 2>/dev/null || echo "(psql not available, skipping table verification)"
