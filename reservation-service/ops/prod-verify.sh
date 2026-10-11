#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"
OPS_COMMAND=("ops/prod-verify.sh" "$@")

# Read-only integrity check. It answers "is production internally consistent",
# not "did you choose the right records to keep" — that is a product decision
# and this script does not judge it.

# An explicit database argument means we are inspecting a scratch copy on behalf
# of prod-migrate.sh --dry-run. That must not overwrite the real report or add a
# record claiming production was verified.
DATABASE="${1:-$PROD_DATABASE}"
PREVIEW=0
[[ "$DATABASE" != "$PROD_DATABASE" ]] && PREVIEW=1

require_postgres
require_prod_running
start=$(date +%s)

declare -a CHECK_IDS=(
  "no_duplicate_active_reservation"
  "active_within_capacity"
  "available_slots_matches_active_count"
  "available_slots_within_range"
  "cancelled_has_timestamp"
  "active_has_no_timestamp"
  "status_domain"
)
declare -a CHECK_SQL=(
  "SELECT count(*) FROM (SELECT 1 FROM reservations WHERE status = 'active' GROUP BY user_id, session_id HAVING count(*) > 1) AS offenders"
  "SELECT count(*) FROM sessions s WHERE (SELECT count(*) FROM reservations r WHERE r.session_id = s.id AND r.status = 'active') > s.capacity"
  "SELECT count(*) FROM sessions s WHERE s.available_slots <> s.capacity - (SELECT count(*) FROM reservations r WHERE r.session_id = s.id AND r.status = 'active')"
  "SELECT count(*) FROM sessions WHERE available_slots < 0 OR available_slots > capacity"
  "SELECT count(*) FROM reservations WHERE status = 'cancelled' AND cancelled_at IS NULL"
  "SELECT count(*) FROM reservations WHERE status = 'active' AND cancelled_at IS NOT NULL"
  "SELECT count(*) FROM reservations WHERE status NOT IN ('active', 'cancelled')"
)
declare -a CHECK_LABEL=(
  "no user holds two active reservations for one session"
  "no session has more active reservations than capacity"
  "available_slots agrees with the active reservation count"
  "available_slots stays between 0 and capacity"
  "every cancelled reservation has a cancellation time"
  "no active reservation carries a cancellation time"
  "every reservation status is a known value"
)

query() {
  if [[ "$DATABASE" == "$PROD_DATABASE" ]]; then
    prod_query "$1"
  else
    prod_query_owner "$1" "$DATABASE"
  fi
}

revision="$(query "SELECT version_num FROM alembic_version" | tr -d '[:space:]')"
echo "database: $DATABASE    revision: $revision"
echo

failed=0
results_json=""
for index in "${!CHECK_IDS[@]}"; do
  offenders="$(query "${CHECK_SQL[$index]}" | tr -d '[:space:]')"
  if [[ "$offenders" == "0" ]]; then
    status="pass"
    printf '  PASS  %s\n' "${CHECK_LABEL[$index]}"
  else
    status="fail"
    failed=1
    printf '  FAIL  %s (%s offending rows)\n' "${CHECK_LABEL[$index]}" "$offenders"
  fi
  [[ -n "$results_json" ]] && results_json+=", "
  results_json+="$(printf '{"id": "%s", "status": "%s", "offending_rows": %s}' \
    "${CHECK_IDS[$index]}" "$status" "$offenders")"
done

# Reported as facts against the recorded starting state, not graded.
removed="$(query "SELECT (SELECT count(*) FROM reservations) || ' reservations, ' || (SELECT count(*) FROM reservation_audits) || ' audit rows'")"
echo
echo "  now holding: $removed"

overall="pass"
[[ $failed -eq 0 ]] || overall="fail"

echo
if [[ $PREVIEW -eq 1 ]]; then
  if [[ $failed -eq 0 ]]; then
    echo "$DATABASE is internally consistent."
  else
    echo "$DATABASE is NOT consistent."
  fi
  exit $failed
fi

report="$OPS_DIR/prod-verify-report.json"
printf '{"format": "slotwise-prod-verify-v1", "database": "%s", "revision": "%s", "status": "%s", "checks": [%s]}\n' \
  "$DATABASE" "$revision" "$overall" "$results_json" > "$report"

if [[ $failed -eq 0 ]]; then
  echo "Production is internally consistent. Report: ops/prod-verify-report.json"
else
  echo "Production is NOT consistent. Report: ops/prod-verify-report.json" >&2
fi

append_access_record "prod_verify" "read-only" "$([[ $failed -eq 0 ]] && echo ok || echo failed)" \
  "$failed" "$(( $(date +%s) - start ))" "$revision" "$revision" "none" "" ""
exit $failed
