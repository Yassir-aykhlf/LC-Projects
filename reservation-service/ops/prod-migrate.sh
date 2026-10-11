#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

usage() {
  cat >&2 <<'USAGE'
usage: ./ops/prod-migrate.sh --dry-run [--note "<text>"]
       ./ops/prod-migrate.sh --apply   [--yes] [--note "<text>"]

  --dry-run  Copy production into a scratch database, run the migration there,
             and print exactly what would change. Production is not touched.
  --apply    Run the migration against production.
  --yes      Skip the typed confirmation. Recorded in ops/prod-access.log.
  --note     One line describing why this change is being made.
USAGE
  exit 2
}

MODE=""
ASSUME_YES=0
OPS_NOTE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) [[ -n "$MODE" ]] && usage; MODE="dry-run"; shift ;;
    --apply)   [[ -n "$MODE" ]] && usage; MODE="apply"; shift ;;
    --yes)     ASSUME_YES=1; shift ;;
    --note)    OPS_NOTE="${2:-}"; [[ -z "$OPS_NOTE" ]] && usage; shift 2 ;;
    *)         usage ;;
  esac
done
[[ -n "$MODE" ]] || usage
OPS_COMMAND=("ops/prod-migrate.sh" "--$MODE")
[[ $ASSUME_YES -eq 1 ]] && OPS_COMMAND+=("--yes")
[[ -n "$OPS_NOTE" ]] && OPS_COMMAND+=("--note" "$OPS_NOTE")

require_postgres
require_prod_running
require_prod_database

revision_before="$(prod_revision)"

state_dump() {
  # $1 = database name
  prod_query_owner "
    SELECT 'reservation ' || id || ' ' || status || ' ' ||
           coalesce(cancelled_at::text, '-')
    FROM reservations ORDER BY id
  " "$1"
  prod_query_owner "
    SELECT 'session ' || id || ' available_slots ' || available_slots
    FROM sessions ORDER BY id
  " "$1"
}

run_alembic_against() {
  # $1 = database name
  # Alembic reads the working tree directly, so your latest migration file is
  # always the one that runs.
  ( cd "$CANDIDATE_ROOT/backend" \
    && DATABASE_URL="postgresql+psycopg://${SLOTWISE_APP_DATABASE_USER}:${SLOTWISE_APP_DATABASE_PASSWORD}@$PGHOST:$PGPORT/$1" \
       SLOTWISE_ALLOW_PRODUCTION=1 \
       PGOPTIONS='-c default_transaction_read_only=off' \
       "$PYTHON" -m alembic upgrade head )
}

# ---------------------------------------------------------------- dry run ----
if [[ "$MODE" == "dry-run" ]]; then
  start=$(date +%s)
  banner "DRY RUN — production will not be modified"

  dump_file="$(mktemp "${TMPDIR:-/tmp}/slotwise-prod-dryrun.XXXXXX.sql")"
  reset_dry_run() {
    PGOPTIONS='-c default_transaction_read_only=off' \
    PGPASSWORD="$SLOTWISE_APP_DATABASE_PASSWORD" \
      psql -q -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" \
        -U "$SLOTWISE_APP_DATABASE_USER" -d "$DRY_RUN_DATABASE" \
        -c "DROP SCHEMA public CASCADE" \
        -c "CREATE SCHEMA public AUTHORIZATION $SLOTWISE_APP_DATABASE_USER" \
        -c "REVOKE ALL ON SCHEMA public FROM PUBLIC" >/dev/null
  }
  cleanup_dry_run() {
    reset_dry_run 2>/dev/null || true
    rm -f "$dump_file"
  }
  trap cleanup_dry_run EXIT

  PGPASSWORD="$SLOTWISE_APP_DATABASE_PASSWORD" \
    pg_dump --no-owner --no-privileges -h "$PGHOST" -p "$PGPORT" \
      -U "$SLOTWISE_APP_DATABASE_USER" -d "$PROD_DATABASE" \
      --file "$dump_file"
  reset_dry_run
  PGPASSWORD="$SLOTWISE_APP_DATABASE_PASSWORD" \
    psql -q -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" \
      -U "$SLOTWISE_APP_DATABASE_USER" -d "$DRY_RUN_DATABASE" \
      -f "$dump_file" >/dev/null
  rm -f "$dump_file"

  before="$(state_dump "$DRY_RUN_DATABASE")"
  set +e
  migrate_output="$(run_alembic_against "$DRY_RUN_DATABASE" 2>&1)"
  code=$?
  set -e
  echo "$migrate_output"
  echo

  if [[ $code -ne 0 ]]; then
    echo "The migration FAILED on the copy. Production is unchanged." >&2
    append_access_record "prod_migrate" "dry-run" "failed" "$code" \
      "$(( $(date +%s) - start ))" "$revision_before" "$revision_before" "none" "" ""
    exit $code
  fi

  after="$(state_dump "$DRY_RUN_DATABASE")"
  mkdir -p "$DRY_RUN_DIR"
  diff_file="$DRY_RUN_DIR/$(date -u +%Y%m%dT%H%M%SZ).diff"
  diff -u <(printf '%s\n' "$before") <(printf '%s\n' "$after") > "$diff_file" || true

  echo "What this migration would change in production:"
  echo
  if [[ -s "$diff_file" ]]; then
    sed 's/^/  /' "$diff_file"
  else
    echo "  (no row-level changes)"
  fi
  echo
  echo "Invariant check against the migrated copy:"
  "$OPS_DIR/prod-verify.sh" "$DRY_RUN_DATABASE" | sed 's/^/  /' || true
  echo
  echo "Saved to ${diff_file#"$CANDIDATE_ROOT/"}. Read it before running --apply."

  append_access_record "prod_migrate" "dry-run" "ok" 0 \
    "$(( $(date +%s) - start ))" "$revision_before" "$revision_before" "none" "" ""
  exit 0
fi

# ------------------------------------------------------------------ apply ----
banner "PRODUCTION CHANGE — this modifies real records"
echo "  database:  $PROD_DATABASE"
echo "  revision:  $revision_before"
prod_query "
  SELECT format('  %-20s %s rows', 'reservations', count(*)) FROM reservations
"
echo

if ! log_has_successful "prod_migrate" "dry-run"; then
  echo "  WARNING: no successful dry run is recorded. You are about to change"
  echo "           production without having seen what will change."
fi
if [[ ! -f "$REHEARSAL_STATE" ]]; then
  echo "  WARNING: no local rehearsal is recorded. ./ops/local-restore-snapshot.sh"
  echo "           loads a production snapshot into local so you can try first."
fi

confirmation_method="none"
confirmation_value=""
if [[ $ASSUME_YES -eq 1 ]]; then
  confirmation_method="flag"
  echo "  Proceeding because --yes was passed."
elif [[ -t 0 ]]; then
  printf '  Type %s to continue: ' "$CONFIRMATION_PHRASE"
  read -r typed
  if [[ "$typed" != "$CONFIRMATION_PHRASE" ]]; then
    echo "  Confirmation did not match. Nothing was changed."
    exit 1
  fi
  confirmation_method="typed"
  confirmation_value="$typed"
else
  echo "  WARNING: non-interactive execution; no human confirmation was captured."
  echo "           Continuing anyway."
fi

echo
start=$(date +%s)
set +e
run_alembic_against "$PROD_DATABASE"
code=$?
set -e
revision_after="$(prod_revision)"

# Production lives in a database server that a workspace rebuild discards.
# Checkpoint it into the workspace so a rebuild cannot silently undo this change.
prod_checkpoint

append_access_record "prod_migrate" "apply" \
  "$([[ $code -eq 0 ]] && echo ok || echo failed)" "$code" \
  "$(( $(date +%s) - start ))" "$revision_before" "$revision_after" \
  "$confirmation_method" "$confirmation_value" ""

echo
if [[ $code -eq 0 ]]; then
  echo "Production is now at revision $revision_after."
  echo "Now run ./ops/prod-verify.sh and record the change in ops/prod-change-log.md."
else
  echo "The migration failed. Production reports revision $revision_after." >&2
  echo "Check what state it is in before retrying." >&2
fi
exit $code
