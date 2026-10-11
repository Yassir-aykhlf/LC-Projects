# SlotWise environment. Sourced by every script here, by ops/_lib.sh, and by
# each new terminal (see .theia/horizon.json terminalInitCommand).
#
# Exports only. No `set -e`, no `exit`, no side effects — sourcing this must
# never be able to kill an interactive shell.

SLOTWISE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export SLOTWISE_ROOT

# The virtualenv lives at the workspace root, named `venv`, which is what the
# submission harness expects to find and activate. It is excluded from the
# storage sync, so it is rebuilt by .theia/setup.sh whenever the workspace
# comes back.
export SLOTWISE_VENV="${SLOTWISE_VENV:-$SLOTWISE_ROOT/venv}"

# One PostgreSQL server, three databases. The server runs beside this
# workspace and is already accepting connections before the IDE opens; this
# container has the client tools only, so there is no PGDATA and no server
# binaries here.
#
# Both keep the `:-` form on purpose: the submission harness overrides them to
# point these scripts at its own cluster, and they are what makes everything
# here work on a developer machine too.
export PGHOST="${PGHOST:-127.0.0.1}"
export PGPORT="${PGPORT:-5432}"

export SLOTWISE_LOCAL_DATABASE="${SLOTWISE_LOCAL_DATABASE:-slotwise_local}"
export SLOTWISE_TEST_DATABASE="${SLOTWISE_TEST_DATABASE:-slotwise_test}"
export SLOTWISE_PROD_DATABASE="${SLOTWISE_PROD_DATABASE:-slotwise_prod}"

# Candidate-visible credentials for ordinary roles created by .sandbox's
# PostgreSQL initdb script. None has SUPERUSER, CREATEDB or CREATEROLE. The
# platform administrator and grading credentials are intentionally absent.
export SLOTWISE_DATABASE_USER="slotwise"
export SLOTWISE_DATABASE_PASSWORD="slotwise"
export SLOTWISE_APP_DATABASE_USER="slotwise_app"
export SLOTWISE_APP_DATABASE_PASSWORD="slotwise_app"
export SLOTWISE_READONLY_DATABASE_USER="slotwise_readonly"
export SLOTWISE_READONLY_DATABASE_PASSWORD="slotwise_readonly"

# Set unconditionally so an ambient image/service value cannot retarget the
# application. Scripts that need another database pass DATABASE_URL inline.
export DATABASE_URL="postgresql+psycopg://${SLOTWISE_DATABASE_USER}:${SLOTWISE_DATABASE_PASSWORD}@${PGHOST}:${PGPORT}/${SLOTWISE_LOCAL_DATABASE}"

if [ -x "$SLOTWISE_VENV/bin/python" ]; then
  export PYTHON="$SLOTWISE_VENV/bin/python"
  case ":$PATH:" in
    *":$SLOTWISE_VENV/bin:"*) ;;
    *) PATH="$SLOTWISE_VENV/bin:$PATH"; export PATH ;;
  esac
else
  PYTHON="$(command -v python3 || true)"
  export PYTHON
fi
