#!/usr/bin/env bash
# Wipe the local database and rebuild it with clean demo data.
#
# Local is yours: reset it as often as you like. This script refuses to touch
# any other database, and there is deliberately no equivalent for production.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source scripts/_env.sh

if [[ "$SLOTWISE_LOCAL_DATABASE" == "$SLOTWISE_PROD_DATABASE" ]]; then
    echo "Refusing to reset: the local database name resolves to production." >&2
    exit 2
fi

echo "Resetting schema in $SLOTWISE_LOCAL_DATABASE"
PGPASSWORD="$SLOTWISE_DATABASE_PASSWORD" \
psql -q -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" \
    -U "$SLOTWISE_DATABASE_USER" -d "$SLOTWISE_LOCAL_DATABASE" \
    -c "DROP SCHEMA public CASCADE" \
    -c "CREATE SCHEMA public AUTHORIZATION $SLOTWISE_DATABASE_USER" \
    -c "REVOKE ALL ON SCHEMA public FROM PUBLIC" >/dev/null

( cd backend && "$PYTHON" -m alembic upgrade head >/dev/null )
PYTHONPATH=backend "$PYTHON" -m app.seed

echo "$SLOTWISE_LOCAL_DATABASE now holds clean demo data."
