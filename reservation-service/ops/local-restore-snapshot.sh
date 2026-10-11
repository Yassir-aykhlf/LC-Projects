#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"
OPS_COMMAND=("ops/local-restore-snapshot.sh" "$@")

# Load the production snapshot into the LOCAL database so a change can be
# rehearsed before it runs against production. This wipes local; that is what
# local is for.

require_postgres
require_local_database
start=$(date +%s)

echo "Restoring ops/prod-snapshot.sql into $LOCAL_DATABASE."
echo "This replaces everything currently in the local database."

PGPASSWORD="$SLOTWISE_DATABASE_PASSWORD" \
psql -qtAX -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" \
  -U "$SLOTWISE_DATABASE_USER" -d "$LOCAL_DATABASE" \
  -c "DROP SCHEMA public CASCADE" \
  -c "CREATE SCHEMA public AUTHORIZATION $SLOTWISE_DATABASE_USER" \
  -c "REVOKE ALL ON SCHEMA public FROM PUBLIC" >/dev/null

PGPASSWORD="$SLOTWISE_DATABASE_PASSWORD" \
psql -q -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" \
  -U "$SLOTWISE_DATABASE_USER" -d "$LOCAL_DATABASE" \
  -f "$OPS_DIR/prod-snapshot.sql" >/dev/null

snapshot_sha="$(sha256_of "$(cat "$OPS_DIR/prod-snapshot.sql")")"
printf '{"ts": "%s", "snapshot_sha256": "%s", "local_database": "%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$snapshot_sha" "$LOCAL_DATABASE" \
  > "$REHEARSAL_STATE"

echo
echo "Local now holds the snapshot at revision 0001_initial."
echo "Rehearse your change against it, for example:"
echo "  (cd backend && alembic upgrade head)"

append_access_record "local_restore_snapshot" "read-only" "ok" 0 \
  "$(( $(date +%s) - start ))" "" "" "none" "" ""
