
# SlotWise

SlotWise is a small course and event reservation service. Users can browse
upcoming sessions and remaining capacity, reserve or cancel a place, and view
their active and cancelled reservations on the Dashboard.

You have just taken over this live service from Robin, the engineer who built
and ran it. Robin has moved to another team and answers product questions in
the handover Q&A channel for the rest of this window; they no longer have
access to the repository and cannot debug it for you.

## Production incident: reservation state is unreliable

The handover left no trusted diagnosis behind — only a small test suite and a
few sanitized support artifacts.

Recent support reports suggest the reservation experience is no longer
reliable. Investigate the application, confirm the causes, fix the defects, and
add useful regression tests.

Keep the existing public API compatible while making the system reliable.

SlotWise runs more than one database: a local one you can reset freely, and the
production database, which holds real historical records and has no reset path.
The production data is known to be inconsistent and must be repaired in place;
finish by applying your repair to production and verifying the result.

## Task scope

This production incident is confined to the **backend and persistence layer**.
`frontend/` is an observation and reproduction surface; completing the task
does not require frontend changes.

The environment, the run and migration harness, and the production audit trail
are write-protected in this workspace: if a file cannot be edited, it is not
part of the incident. Everything else is yours to change.

### What must stay compatible

Refactor internals however you like — but your code is imported, started, and
exercised from outside, by test suites you cannot see. Renaming or resigning
anything below reads as a broken submission, not as a design choice.

- **HTTP API** — same paths, methods, status codes, and response fields,
  including reservation creation nested under its session URL and the
  `X-User-ID` authentication header.
- **Application wiring** — `app.main.create_app(database_url)` returns a FastAPI
  app exposing `app.state.engine` and `app.state.SessionLocal`; `app.db.Base` is
  the declarative base whose metadata covers every table;
  `app.db.assert_not_production(...)` keeps honouring the
  `SLOTWISE_ALLOW_PRODUCTION=1` override for operations that pass
  `allow_override=True` and keeps refusing it for destructive fixtures;
  `app.seed.seed(db)` seeds demo data into an already-migrated database.
- **Service layer** — `app.services.reservation_service` keeps the signatures of
  its public functions stable: same module, same names, same keyword arguments,
  same exception types. What they do inside is yours to change.
- **Models** — `app.models` keeps exporting `EventSession`, `Reservation`, and
  `ReservationAudit`, backed by the `sessions`, `reservations`, and
  `reservation_audits` tables. Existing column names keep their meaning, and the
  stored status and action strings stay as they are today (`"active"`,
  `"cancelled"`). Adding columns, constraints, or indexes is expected — via a new
  migration.
- **Response schemas** — in `backend/app/schemas.py` you may **add** optional
  fields. Do not rename, retype, or remove an existing one; clients and the test
  suites read the current shapes.
- **Migrations** — Alembic runs from `backend/` with `DATABASE_URL` in the
  environment, and `alembic upgrade head` must reach a schema your application
  works against. `0001_initial` is already applied in production: do not modify
  or rename it, add a new revision on top.
- **Test fixtures** — you may add fixtures to `tests/conftest.py`, but keep the
  `assert_not_production(...)` guard and the truncate-and-seed fixture intact.
  That suite empties every table, and the guard is what stops it reaching a real
  database.
- **Dependencies** — your environment and the grading run both install from
  `backend/requirements.lock` and `backend/requirements-test.lock`, so a change
  there must keep `./scripts/run-local.sh` and `./scripts/test-postgres.sh`
  working. Prefer solving the incident with what is already installed.

## Incident materials

The sanitized request log and support cases below were attached to the handoff.
They are incomplete, may overlap, and do not contain a trusted diagnosis. Start
the application as described below and investigate the reports using the UI,
API, code, and tests.

### Sanitized support cases

**SW-1842** — Ada encountered a slow response while booking. What she later saw
in the Dashboard did not match what she expected.

**SW-1849** — During a busy session release, customers and support staff
reported conflicting information about whether places were still available.

**SW-1857** — A customer contacted support after a cancellation because
different parts of the product appeared to disagree.

Operations confirmed that the production database has to stay available at all
times, so resetting it is not permitted — it is never a recovery step. They also
report that some historical reservation records in production no longer agree
with what the product shows, and that this has to be corrected in place.

### Sanitized request log

```text
2026-08-02T09:15:31Z INFO request_id=req_demo_01 user=1 POST /api/sessions/2/reservations status=201 duration_ms=802
2026-08-02T09:15:32Z INFO request_id=req_demo_02 user=1 POST /api/sessions/2/reservations status=201 duration_ms=31 retry_of=req_demo_01
2026-08-03T13:40:08Z INFO request_id=req_demo_03 user=1 POST /api/reservations/7/cancel status=200 duration_ms=19
2026-08-03T13:40:09Z INFO request_id=req_demo_04 user=1 POST /api/reservations/7/cancel status=200 duration_ms=17 retry_of=req_demo_03
2026-08-04T04:02:55Z ERROR request_id=req_demo_05 user=2 POST /api/sessions/999999/reservations status=500 error=internal_server_error
```

All names, tokens, addresses, and request IDs in these assets are synthetic.

## Repository guide

The main request flow is:

```text
FastAPI routes -> reservation service -> SQLAlchemy -> PostgreSQL
```

- `EventSession` is a bookable course or event session with capacity and
  remaining-slot information.
- `Reservation` records one user's place in a session and is either `active` or
  `cancelled`.
- Development authentication uses the `X-User-ID` header; the UI can switch
  between demo users.

### Backend guide

- `app/api/sessions.py` lists bookable sessions.
- `app/api/reservations.py` creates, lists, and cancels reservations. The public
  API still keeps reservation creation nested beneath its session URL.
- `app/services/reservation_service.py` owns reservation lifecycle and
  transaction behavior.
- `create_app()` assembles FastAPI middleware, routes, the database engine, and
  the request-scoped session factory. It does not create schemas or write demo
  data.
- `create_database_engine()` validates the PostgreSQL URL and creates a
  SQLAlchemy engine with connection health checks.
- `app/seed.py` is the post-migration demo-data command for the **local**
  database. There is no hidden reset path in the application, and no seed
  command that would rebuild production.

## Environments

SlotWise runs against more than one database. Which one you are talking to
matters, so they are named differently everywhere.

| Environment | Database | How it starts | Contents | Can it be reset? |
| --- | --- | --- | --- | --- |
| **local** | `slotwise_local` | `./scripts/run-local.sh` | Clean demo data | **Yes.** `./scripts/local-reset.sh` |
| **test** | `slotwise_test` | `./scripts/test-postgres.sh` | Rebuilt every run | **Yes**, automatically |
| **production** | `slotwise_prod` | `./ops/prod-up.sh` | Real historical records | **No.** There is no reset command |

The application connects to **local**. All three databases live in one
PostgreSQL cluster, separated by permission rather than convention: production
is read-only by default and the local role cannot connect to it at all, so
nothing you do to local can reach it. Full details are in
[`ops/README.md`](ops/README.md).

## Start the local environment

PostgreSQL runs as its own service beside this workspace and is already
accepting connections when the IDE opens. Your Python environment and the three
databases are prepared at the same time. If the Python environment or a database
ever looks missing, run **Re-run initialization** from the IDE's quick actions
to prepare them again — the database server itself is not something you start or
stop from here.

```bash
./scripts/run-local.sh
```

This applies Alembic migrations to `slotwise_local`, inserts any missing demo
data, and starts FastAPI. One process serves both the API and the observation
UI:

- UI: <http://localhost:8080/>
- API docs: <http://localhost:8080/docs>
- Demo users: `1` (Ada), `2` (Lin), and `3` (Sam)

Stop it with Ctrl-C; local data is preserved. To wipe local and rebuild it with
clean demo data:

```bash
./scripts/local-reset.sh
```

That only ever touches **local**. It cannot reach production — the local role
has no access to it. Reset local as often as you like.

## The production environment

Production holds real reservation history and is known to contain inconsistent
records that must be repaired in place. It has no reset path — if you damage it,
it stays damaged.

Read it freely; a read-only role is provided:

```bash
./ops/prod-up.sh        # start it, print revision and row counts
./ops/prod-status.sh    # sessions, capacity, availability, active counts
./ops/prod-psql.sh -c "SELECT * FROM reservations ORDER BY id"
```

Rehearse before you write. `ops/prod-snapshot.sql` is a sanitized extract of
production that loads into local:

```bash
./ops/local-restore-snapshot.sh
```

It is an extract, not a copy: production contains records the snapshot does not.

Then preview and apply:

```bash
./ops/prod-migrate.sh --dry-run   # copies production, migrates the copy,
                                  # prints the exact diff, discards it
./ops/prod-migrate.sh --apply
./ops/prod-verify.sh              # read-only consistency check
```

Record what you did in [`ops/prod-change-log.md`](ops/prod-change-log.md), and
keep `ops/prod-access.log`, `ops/prod-verify-report.json` and `ops/dry-runs/` in
your submission.

Two constraints worth knowing:

- Production records Alembic revision `0001_initial`. Migrations already applied
  there must not be renamed or rewritten; add new ones.
- The application refuses to start against `slotwise_prod` and the test suites
  refuse to run against it, because the visible test fixture truncates every
  table.

## Run tests

All API and integration tests run against a disposable `slotwise_test`
database, which is dropped and rebuilt at the start of every run:

```bash
./scripts/test-postgres.sh
```

JUnit evidence is written to `artifacts/postgres-visible.xml`. Add or change
valuable regression tests as part of your investigation.

## Handover Q&A

Parts of the specification were never written down; they only exist in Robin's
memory. When a product behavior is genuinely ambiguous, ask Robin in the
handover Q&A (Ask) channel. They can tell you what SlotWise was supposed to do.
They no longer have access to the repository or to production, cannot run
anything, and cannot tell you where a defect is. If the specification never covered
your question, they will say so and ask you to make a reasonable choice and
document it.

## Your coding agent

`opencode.json` holds your coding agent's permissions. It ships asking for
approval before every edit and every shell command. Loosening it is your call
and is visible in your session; deciding what the agent may do without asking is
part of the work, not a detail.

## Review your changes

This workspace is a Git repository with the starting snapshot committed on
`main`. Use the normal commands while you work:

```bash
git status
git diff
```

Generated dependencies, test evidence, and build output are ignored.

Everything in this workspace is part of your submission, including your
production change log and the generated records under `ops/`. There is nothing
to package by hand.
