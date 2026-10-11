#!/usr/bin/env bash
# Start SlotWise against the local database.
#
# One process serves both the JSON API and the observation UI on port 8080 —
# the single application port the sandbox publishes.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source scripts/_env.sh

PORT="${SLOTWISE_PORT:-8080}"

if ! pg_isready -h "$PGHOST" -p "$PGPORT" -q 2>/dev/null; then
    echo "PostgreSQL is not accepting connections on $PGHOST:$PGPORT." >&2
    echo "It runs beside this workspace and is not started from here — wait a" >&2
    echo "moment and retry, then reload the workspace if it stays down." >&2
    exit 2
fi

( cd backend && "$PYTHON" -m alembic upgrade head )
PYTHONPATH=backend "$PYTHON" -m app.seed

echo
echo "SlotWise is starting on http://localhost:$PORT"
echo "  UI        http://localhost:$PORT/"
echo "  API docs  http://localhost:$PORT/docs"
echo "  Demo users: 1 (Ada), 2 (Lin), 3 (Sam) via the X-User-ID header"
echo

exec "$PYTHON" -m uvicorn --app-dir backend app.main:app \
    --host 0.0.0.0 --port "$PORT"
