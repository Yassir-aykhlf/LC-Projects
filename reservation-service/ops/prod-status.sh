#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"
OPS_COMMAND=("ops/prod-status.sh" "$@")

require_postgres
require_prod_running
start=$(date +%s)
revision="$(prod_revision)"

echo "database: $PROD_DATABASE    revision: $revision"
echo
echo "sessions:"
prod_query "
  SELECT format('  %-4s %-30s capacity %-3s available %-3s active %s',
                s.id, s.title, s.capacity, s.available_slots,
                (SELECT count(*) FROM reservations r
                  WHERE r.session_id = s.id AND r.status = 'active'))
  FROM sessions s ORDER BY s.id
"
echo
echo "reservations by status:"
prod_query "
  SELECT format('  %-10s %s', status, count(*))
  FROM reservations GROUP BY status ORDER BY status
"

append_access_record "prod_status" "read-only" "ok" 0 "$(( $(date +%s) - start ))" \
  "$revision" "$revision" "none" "" ""
