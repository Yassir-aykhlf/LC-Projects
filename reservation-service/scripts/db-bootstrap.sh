#!/usr/bin/env bash
# Initialize content inside databases pre-created by .sandbox's PostgreSQL
# initdb script. This runs only as ordinary database owners and never creates
# roles or databases.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source scripts/_env.sh

psql_as() {
    local user="$1" password="$2" database="$3"
    shift 3
    PGPASSWORD="$password" psql -qtAX -v ON_ERROR_STOP=1 \
        -h "$PGHOST" -p "$PGPORT" -U "$user" -d "$database" "$@"
}

require_identity() {
    local user="$1" password="$2" database="$3" actual
    actual="$(psql_as "$user" "$password" "$database" \
        -c "SELECT current_user || '|' || current_database()" | tr -d '[:space:]')"
    if [[ "$actual" != "$user|$database" ]]; then
        echo "Expected $user@$database, reached $actual" >&2
        exit 2
    fi
}

require_identity "$SLOTWISE_DATABASE_USER" "$SLOTWISE_DATABASE_PASSWORD" "$SLOTWISE_LOCAL_DATABASE"
require_identity "$SLOTWISE_DATABASE_USER" "$SLOTWISE_DATABASE_PASSWORD" "$SLOTWISE_TEST_DATABASE"
require_identity "$SLOTWISE_APP_DATABASE_USER" "$SLOTWISE_APP_DATABASE_PASSWORD" "$SLOTWISE_PROD_DATABASE"

# Local is idempotently migrated and seeded on every workspace setup.
local_url="postgresql+psycopg://${SLOTWISE_DATABASE_USER}:${SLOTWISE_DATABASE_PASSWORD}@$PGHOST:$PGPORT/$SLOTWISE_LOCAL_DATABASE"
( cd backend && DATABASE_URL="$local_url" "$PYTHON" -m alembic upgrade head >/dev/null )
DATABASE_URL="$local_url" PYTHONPATH=backend "$PYTHON" -m app.seed

# Production is pre-created but populated exactly once for this sidecar. A
# restored workspace supplies a checkpoint; a new workspace gets the fixture.
prod_initialized="$(psql_as \
    "$SLOTWISE_APP_DATABASE_USER" "$SLOTWISE_APP_DATABASE_PASSWORD" \
    "$SLOTWISE_PROD_DATABASE" \
    -c "SELECT to_regclass('public.alembic_version') IS NOT NULL" \
    | tr -d '[:space:]')"
if [[ "$prod_initialized" == "t" ]]; then
    exit 0
fi

export PGOPTIONS='-c default_transaction_read_only=off'
PGPASSWORD="$SLOTWISE_APP_DATABASE_PASSWORD" \
    psql -q -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" \
    -U "$SLOTWISE_APP_DATABASE_USER" -d "$SLOTWISE_PROD_DATABASE" \
    -f ops/prod-init/00-roles.sql >/dev/null

if [[ -s ops/.prod-restore.sql ]]; then
    echo "Restoring $SLOTWISE_PROD_DATABASE from ops/.prod-restore.sql"
    PGPASSWORD="$SLOTWISE_APP_DATABASE_PASSWORD" \
        psql -q -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" \
        -U "$SLOTWISE_APP_DATABASE_USER" -d "$SLOTWISE_PROD_DATABASE" \
        -f ops/.prod-restore.sql >/dev/null
else
    echo "Provisioning $SLOTWISE_PROD_DATABASE from ops/prod-init/"
    for fixture in ops/prod-init/10-legacy-schema.sql ops/prod-init/20-legacy-data.sql; do
        PGPASSWORD="$SLOTWISE_APP_DATABASE_PASSWORD" \
            psql -q -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" \
            -U "$SLOTWISE_APP_DATABASE_USER" -d "$SLOTWISE_PROD_DATABASE" \
            -f "$fixture" >/dev/null
    done
fi

# Cover restored or pre-existing objects as well as future objects handled by
# ALTER DEFAULT PRIVILEGES in 00-roles.sql.
psql_as "$SLOTWISE_APP_DATABASE_USER" "$SLOTWISE_APP_DATABASE_PASSWORD" \
    "$SLOTWISE_PROD_DATABASE" \
    -c "GRANT USAGE ON SCHEMA public TO $SLOTWISE_READONLY_DATABASE_USER" \
    -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO $SLOTWISE_READONLY_DATABASE_USER" \
    -c "GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO $SLOTWISE_READONLY_DATABASE_USER" \
    -c "ALTER DATABASE $SLOTWISE_PROD_DATABASE SET default_transaction_read_only = on" \
    >/dev/null

unset PGOPTIONS
echo "Production is provisioned. It has no reset path — see ops/README.md."
