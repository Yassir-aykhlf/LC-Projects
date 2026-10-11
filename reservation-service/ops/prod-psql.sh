#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"
OPS_COMMAND=("ops/prod-psql.sh" "$@")

ROLE="$SLOTWISE_READONLY_DATABASE_USER"
ROLE_PASSWORD="$SLOTWISE_READONLY_DATABASE_PASSWORD"
if [[ "${1:-}" == "--role" ]]; then
  case "${2:-}" in
    app) ROLE="$SLOTWISE_APP_DATABASE_USER"; ROLE_PASSWORD="$SLOTWISE_APP_DATABASE_PASSWORD"; shift 2 ;;
    readonly) shift 2 ;;
    *) echo "usage: $0 [--role readonly|app] [psql args...]" >&2; exit 2 ;;
  esac
fi

require_postgres
require_prod_running
start=$(date +%s)
revision="$(prod_revision)"
export PGPASSWORD="$ROLE_PASSWORD"

if [[ "$ROLE" == "$SLOTWISE_APP_DATABASE_USER" ]]; then
  echo "Opening production as the owner role with writes enabled. Writes here" >&2
  echo "bypass ./ops/prod-migrate.sh and leave no change record." >&2
  # Production is read-only by default at the database level; this is one of
  # only two paths that clears it, and it says so out loud.
  export PGOPTIONS='-c default_transaction_read_only=off'
fi

set +e
if [[ -t 0 && $# -eq 0 ]]; then
  psql -h "$PGHOST" -p "$PGPORT" -U "$ROLE" -d "$PROD_DATABASE"
else
  psql -h "$PGHOST" -p "$PGPORT" -U "$ROLE" -d "$PROD_DATABASE" "$@"
fi
code=$?
set -e

[[ "$ROLE" == "$SLOTWISE_APP_DATABASE_USER" ]] && prod_checkpoint

append_access_record "prod_psql" "read-only" \
  "$([[ $code -eq 0 ]] && echo ok || echo failed)" "$code" \
  "$(( $(date +%s) - start ))" "$revision" "$revision" "none" "" ""
exit $code
