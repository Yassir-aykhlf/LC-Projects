#!/usr/bin/env bash
# Shared helpers for the ops scripts. Sourced, not executed.

OPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CANDIDATE_ROOT="$(cd "$OPS_DIR/.." && pwd)"
source "$CANDIDATE_ROOT/scripts/_env.sh"

PROD_DATABASE="$SLOTWISE_PROD_DATABASE"
LOCAL_DATABASE="$SLOTWISE_LOCAL_DATABASE"
DRY_RUN_DATABASE="slotwise_prod_dryrun"
ACCESS_LOG="$OPS_DIR/prod-access.log"
REHEARSAL_STATE="$OPS_DIR/rehearsal-state.json"
RESTORE_POINT="$OPS_DIR/.prod-restore.sql"
DRY_RUN_DIR="$OPS_DIR/dry-runs"
CONFIRMATION_PHRASE="APPLY TO PRODUCTION"
OPS_SCRIPT_VERSION="2"

require_postgres() {
  if ! command -v psql >/dev/null 2>&1; then
    echo "psql is not available in this workspace." >&2
    exit 2
  fi
  if ! pg_isready -h "$PGHOST" -p "$PGPORT" -q 2>/dev/null; then
    echo "PostgreSQL is not accepting connections on $PGHOST:$PGPORT." >&2
    echo "It runs beside this workspace and is not started from here — wait a" >&2
    echo "moment and retry, then reload the workspace if it stays down." >&2
    exit 2
  fi
}

prod_database_exists() {
  local found
  found="$(PGPASSWORD="$SLOTWISE_APP_DATABASE_PASSWORD" \
    psql -qtAX -h "$PGHOST" -p "$PGPORT" \
    -U "$SLOTWISE_APP_DATABASE_USER" -d "$PROD_DATABASE" \
    -c "SELECT current_database()" 2>/dev/null \
    | tr -d '[:space:]')"
  [[ "$found" == "$PROD_DATABASE" ]]
}

prod_database_initialized() {
  local initialized
  initialized="$(PGPASSWORD="$SLOTWISE_APP_DATABASE_PASSWORD" \
    psql -qtAX -h "$PGHOST" -p "$PGPORT" \
    -U "$SLOTWISE_APP_DATABASE_USER" -d "$PROD_DATABASE" \
    -c "SELECT to_regclass('public.alembic_version') IS NOT NULL" \
    2>/dev/null | tr -d '[:space:]')"
  [[ "$initialized" == "t" ]]
}

require_prod_running() {
  if ! prod_database_exists; then
    echo "The production database $PROD_DATABASE does not exist." >&2
    echo "Create it with ./ops/prod-up.sh." >&2
    exit 2
  fi
}

# Read-only query against production, as the read-only role.
prod_query() {
  PGPASSWORD="$SLOTWISE_READONLY_DATABASE_PASSWORD" \
  psql -qtAX -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" \
    -U "$SLOTWISE_READONLY_DATABASE_USER" -d "$PROD_DATABASE" -c "$1"
}

# Query as the owner. Used for the dry-run clone and for maintenance SQL.
# Still read-only: production carries default_transaction_read_only = on.
prod_query_owner() {
  local database="${2:-$PROD_DATABASE}"
  PGPASSWORD="$SLOTWISE_APP_DATABASE_PASSWORD" \
  psql -qtAX -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" \
    -U "$SLOTWISE_APP_DATABASE_USER" -d "$database" -c "$1"
}

# The only helper that can write to production. PGOPTIONS clears the
# database-level read-only default for this one connection.
prod_query_owner_rw() {
  local database="${2:-$PROD_DATABASE}"
  PGOPTIONS='-c default_transaction_read_only=off' \
  PGPASSWORD="$SLOTWISE_APP_DATABASE_PASSWORD" \
  psql -qtAX -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" \
    -U "$SLOTWISE_APP_DATABASE_USER" -d "$database" -c "$1"
}

prod_revision() {
  prod_query "SELECT version_num FROM alembic_version" 2>/dev/null | tr -d '[:space:]'
}

# Checkpoint production so a workspace rebuild cannot silently hand back a
# pristine database. The database server lives outside the synced workspace, but
# this dump does not. Called after every successful write path.
prod_checkpoint() {
  local tmp="$RESTORE_POINT.tmp"
  if PGPASSWORD="$SLOTWISE_APP_DATABASE_PASSWORD" \
     pg_dump --no-owner --no-privileges -h "$PGHOST" -p "$PGPORT" \
       -U "$SLOTWISE_APP_DATABASE_USER" -d "$PROD_DATABASE" \
       --file "$tmp" 2>/dev/null; then
    mv "$tmp" "$RESTORE_POINT"
  else
    rm -f "$tmp"
  fi
}

# --- guards ------------------------------------------------------------------
# These stop "I repaired production" when you actually repaired local, and the
# reverse. They are about aiming at the right database, not about permission.

require_prod_database() {
  local row name user
  row="$(prod_query_owner "SELECT current_database() || '|' || current_user")"
  name="${row%%|*}"
  user="${row##*|}"
  name="$(printf '%s' "$name" | tr -d '[:space:]')"
  user="$(printf '%s' "$user" | tr -d '[:space:]')"
  if [[ "$name" != "$PROD_DATABASE" ]]; then
    echo "Expected the production database $PROD_DATABASE but reached '$name'." >&2
    exit 2
  fi
  # One cluster now holds every database, so confirming the role matters as
  # much as confirming the database name.
  if [[ "$user" != "$SLOTWISE_APP_DATABASE_USER" ]]; then
    echo "Expected to connect as $SLOTWISE_APP_DATABASE_USER but connected as '$user'." >&2
    exit 2
  fi
}

require_local_database() {
  local name
  name="$(PGPASSWORD="$SLOTWISE_DATABASE_PASSWORD" \
    psql -qtAX -h "$PGHOST" -p "$PGPORT" \
    -U "$SLOTWISE_DATABASE_USER" -d "$LOCAL_DATABASE" \
    -c "SELECT current_database()" \
    2>/dev/null | tr -d '[:space:]')"
  if [[ "$name" != "$LOCAL_DATABASE" ]]; then
    echo "Expected the local database $LOCAL_DATABASE but reached '$name'." >&2
    echo "Re-run initialization from the IDE quick actions to recreate it." >&2
    exit 2
  fi
}

# --- access log --------------------------------------------------------------

sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then
    printf '%s' "$1" | sha256sum | cut -d' ' -f1
  elif command -v shasum >/dev/null 2>&1; then
    printf '%s' "$1" | shasum -a 256 2>/dev/null | cut -d' ' -f1
  else
    printf '%s' "$1" | openssl dgst -sha256 | awk '{print $NF}'
  fi
}

json_string() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  value="${value//$'\n'/\\n}"
  value="${value//$'\r'/}"
  value="${value//$'\t'/\\t}"
  printf '"%s"' "$value"
}

json_array_of_strings() {
  local out="[" first=1 item
  for item in "$@"; do
    [[ $first -eq 1 ]] || out+=","
    out+="$(json_string "$item")"
    first=0
  done
  printf '%s]' "$out"
}

log_has_successful() {
  # $1 = event, $2 = mode
  [[ -f "$ACCESS_LOG" ]] || return 1
  grep -q "\"event\": *\"$1\".*\"mode\": *\"$2\".*\"status\": *\"ok\"" "$ACCESS_LOG"
}

log_first_timestamp() {
  # $1 = event, $2 = mode
  [[ -f "$ACCESS_LOG" ]] || return 0
  grep "\"event\": *\"$1\".*\"mode\": *\"$2\".*\"status\": *\"ok\"" "$ACCESS_LOG" \
    | head -1 | sed -n 's/.*"ts": *"\([^"]*\)".*/\1/p'
}

# append_access_record <event> <mode> <status> <exit_code> <duration> \
#                      <revision_before> <revision_after> <confirmation_method> \
#                      <confirmation_value> <detail>
append_access_record() {
  local event="$1" mode="$2" status="$3" exit_code="$4" duration="$5"
  local revision_before="$6" revision_after="$7"
  local confirmation_method="$8" confirmation_value="$9" detail="${10}"

  local stdin_tty="false" stdout_tty="false"
  [[ -t 0 ]] && stdin_tty="true"
  [[ -t 1 ]] && stdout_tty="true"

  local dry_run_seen="false" dry_run_ts="null"
  if log_has_successful "prod_migrate" "dry-run"; then
    dry_run_seen="true"
    dry_run_ts="$(json_string "$(log_first_timestamp "prod_migrate" "dry-run")")"
  fi
  local rehearsal_seen="false" rehearsal_ts="null"
  if [[ -f "$REHEARSAL_STATE" ]]; then
    rehearsal_seen="true"
    rehearsal_ts="$(json_string \
      "$(sed -n 's/.*"ts": *"\([^"]*\)".*/\1/p' "$REHEARSAL_STATE" | head -1)")"
  fi
  local verify_seen="false"
  log_has_successful "prod_verify" "read-only" && verify_seen="true"

  local prev="null"
  if [[ -s "$ACCESS_LOG" ]]; then
    prev="$(json_string "$(sha256_of "$(tail -n 1 "$ACCESS_LOG")")")"
  fi

  local confirmation_json="null"
  [[ "$confirmation_value" != "" ]] && \
    confirmation_json="$(json_string "$confirmation_value")"

  local warnings=()
  if [[ "$mode" == "apply" && "$confirmation_method" != "typed" ]]; then
    warnings+=("non-interactive execution: no human confirmation was captured")
  fi
  if [[ "$mode" == "apply" && "$dry_run_seen" == "false" ]]; then
    warnings+=("no dry run preceded this production write")
  fi
  if [[ "$mode" == "apply" && "$rehearsal_seen" == "false" ]]; then
    warnings+=("no local rehearsal preceded this production write")
  fi

  mkdir -p "$(dirname "$ACCESS_LOG")"
  printf '{"ts": "%s", "event": "%s", "mode": "%s", "script_version": "%s", "command": %s, "operator": {"stdin_tty": %s, "stdout_tty": %s, "user": %s}, "confirmation": {"required_phrase": "%s", "method": "%s", "value_received": %s, "note": %s}, "preconditions": {"dry_run_seen": %s, "dry_run_ts": %s, "local_rehearsal_seen": %s, "local_rehearsal_ts": %s, "prod_verify_seen_before": %s}, "database": {"name": "%s", "revision_before": %s, "revision_after": %s}, "result": {"status": "%s", "exit_code": %s, "duration_seconds": %s}, "warnings": %s, "prev_sha256": %s}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "$event" "$mode" "$OPS_SCRIPT_VERSION" \
    "$(json_array_of_strings "${OPS_COMMAND[@]}")" \
    "$stdin_tty" "$stdout_tty" "$(json_string "${USER:-unknown}")" \
    "$CONFIRMATION_PHRASE" "$confirmation_method" "$confirmation_json" \
    "$(json_string "${OPS_NOTE:-}")" \
    "$dry_run_seen" "$dry_run_ts" "$rehearsal_seen" "$rehearsal_ts" "$verify_seen" \
    "$PROD_DATABASE" \
    "$([[ -n "$revision_before" ]] && json_string "$revision_before" || echo null)" \
    "$([[ -n "$revision_after" ]] && json_string "$revision_after" || echo null)" \
    "$status" "$exit_code" "$duration" \
    "$(json_array_of_strings "${warnings[@]+"${warnings[@]}"}")" \
    "$prev" \
    >> "$ACCESS_LOG"
}

banner() {
  echo
  echo "=============================================================="
  echo "  $1"
  echo "=============================================================="
  echo
}
