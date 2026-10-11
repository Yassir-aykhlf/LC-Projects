#!/usr/bin/env bash
# Run the visible test suite against a disposable PostgreSQL database.
#
# The test database schema is rebuilt at the START of every run, so each run
# gets clean state and a failing run leaves it in place for inspection.
#
# Your submitted tests are re-run with this script exactly as it ships.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source scripts/_env.sh

ARTIFACT="${SLOTWISE_POSTGRES_ARTIFACT:-postgres-visible.xml}"
TEST_DATABASE="$SLOTWISE_TEST_DATABASE"

# This suite truncates every table. Belt and braces alongside the
# assert_not_production() guard in tests/conftest.py.
if [[ "$TEST_DATABASE" == "$SLOTWISE_PROD_DATABASE" ]]; then
    echo "Refusing to run the destructive test suite against $TEST_DATABASE." >&2
    exit 2
fi

if ! command -v psql >/dev/null 2>&1 || ! pg_isready -h "$PGHOST" -p "$PGPORT" -q 2>/dev/null; then
    echo "PostgreSQL is not accepting connections on $PGHOST:$PGPORT." >&2
    echo "It runs beside this workspace and is not started from here — wait a" >&2
    echo "moment and retry, then reload the workspace if it stays down." >&2
    exit 2
fi

PGPASSWORD="$SLOTWISE_DATABASE_PASSWORD" \
psql -q -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" \
    -U "$SLOTWISE_DATABASE_USER" -d "$TEST_DATABASE" \
    -c "DROP SCHEMA public CASCADE" \
    -c "CREATE SCHEMA public AUTHORIZATION $SLOTWISE_DATABASE_USER" \
    -c "REVOKE ALL ON SCHEMA public FROM PUBLIC" >/dev/null

export DATABASE_URL="postgresql+psycopg://${SLOTWISE_DATABASE_USER}:${SLOTWISE_DATABASE_PASSWORD}@$PGHOST:$PGPORT/$TEST_DATABASE"

( cd backend && "$PYTHON" -m alembic upgrade head >/dev/null )

TEST_TARGETS=("$@")
if [[ ${#TEST_TARGETS[@]} -eq 0 ]]; then
    TEST_TARGETS=(tests)
fi

mkdir -p artifacts
status=0
"$PYTHON" -m pytest -q "${TEST_TARGETS[@]}" --junitxml="artifacts/$ARTIFACT" || status=$?

echo
echo "PostgreSQL evidence: artifacts/$ARTIFACT"
exit $status
