#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"
OPS_COMMAND=("ops/prod-up.sh" "$@")

# Production is a database, not a container: there is nothing to boot. This
# makes sure it exists, then reports what is in it.

require_postgres
start=$(date +%s)

if ! prod_database_initialized; then
  echo "Production has not been initialized in this workspace. Provisioning it."
  bash "$CANDIDATE_ROOT/scripts/db-bootstrap.sh"
fi

require_prod_database

revision="$(prod_revision)"
echo "Production is up."
echo "  database:  $PROD_DATABASE"
echo "  revision:  $revision"
echo
echo "Row counts:"
prod_query "
  SELECT '  users              ' || count(*) FROM users
  UNION ALL SELECT '  sessions           ' || count(*) FROM sessions
  UNION ALL SELECT '  reservations       ' || count(*) FROM reservations
  UNION ALL SELECT '  reservation_audits ' || count(*) FROM reservation_audits
"
echo
echo "Read it with ./ops/prod-status.sh or ./ops/prod-psql.sh."

prod_checkpoint

append_access_record "prod_up" "read-only" "ok" 0 "$(( $(date +%s) - start ))" \
  "$revision" "$revision" "none" "" ""
