# Environments and production operations

SlotWise talks to more than one database. Which one you are talking to matters,
so they are named differently everywhere.

| Environment | Database | How it starts | Contents | Can it be reset? |
| --- | --- | --- | --- | --- |
| **local** | `slotwise_local` | `./scripts/run-local.sh` | Clean demo data from `app/seed.py` | **Yes.** `./scripts/local-reset.sh` |
| **test** | `slotwise_test` | `./scripts/test-postgres.sh` | Rebuilt for every run | **Yes**, automatically, every run |
| **production** | `slotwise_prod` | `./ops/prod-up.sh` | Real historical records | **No.** There is no reset command |

All three live in one PostgreSQL server on `127.0.0.1:5432`, which runs beside
this workspace and is already up when the IDE opens. They are separated by
permission, not by convention:

- **Production is read-only by default.** The database carries
  `default_transaction_read_only = on`, so a stray `UPDATE` fails with
  `ERROR: cannot execute UPDATE in a read-only transaction` for normal owner
  connections. Exactly two paths clear it, and both leave a record:
  `./ops/prod-migrate.sh --apply` and `./ops/prod-psql.sh --role app`.
- **The local role cannot reach production at all.** `slotwise` has no
  `CONNECT` privilege on `slotwise_prod`; the attempt fails before you can run
  a query.
- **`slotwise_readonly` can read production and nothing else.**

So `./scripts/local-reset.sh` cannot touch production, and neither can the test
suite, which is why the visible fixture is free to truncate every table.

## Three rules

1. **Local is yours.** Reset it as often as you like.
2. **Production has no undo.** No script here rebuilds it, and there is no seed
   command that would. If you damage it, it stays damaged.
3. **Rehearse before you write.** `ops/prod-snapshot.sql` is an extract of
   production you can load into local. Try the change there, then dry-run it
   against production, then apply it.

## Reading production

```bash
./ops/prod-up.sh          # make sure it exists; print revision and row counts
./ops/prod-status.sh      # sessions, capacities, availability, active counts
./ops/prod-psql.sh        # interactive psql, read-only role
./ops/prod-psql.sh -c "SELECT * FROM reservations ORDER BY id"
```

These use a read-only role. Investigating production is expected and safe.

## Rehearsing

```bash
./ops/local-restore-snapshot.sh       # replaces local with the snapshot
(cd backend && alembic upgrade head)  # try your migration against it
```

The snapshot is an extract, not a copy: names are sanitized and some records
are held back. Production contains rows the snapshot does not. Rehearsing tells
you that a change runs; it does not tell you that you have seen everything it
will touch.

## Changing production

```bash
./ops/prod-migrate.sh --dry-run       # copies production, migrates the copy,
                                      # prints the exact diff, discards it
./ops/prod-migrate.sh --apply         # the real thing
./ops/prod-verify.sh                  # read-only consistency check
```

`--dry-run` is the only way to see what a migration will do to production
without doing it. It takes a consistent `pg_dump` snapshot into the dedicated,
pre-created `slotwise_prod_dryrun` database, migrates that copy, then clears its
schema. It never needs `CREATEDB` or access to the administrator database.
Read its output before applying.

`--apply` asks you to type a confirmation phrase when a terminal is attached.
It does not refuse to run when one is not — an automated caller can proceed,
and `--yes` skips the prompt entirely. What it always does is record the
circumstances.

## What gets recorded

| File | Written by | Contents |
| --- | --- | --- |
| `ops/prod-access.log` | every script here | Append-only JSON lines: what ran, whether a terminal was attached, whether a dry run and a local rehearsal came first, revision before and after |
| `ops/dry-runs/*.diff` | `--dry-run` | The row-level diff each dry run produced |
| `ops/prod-verify-report.json` | `prod-verify.sh` | Result of each consistency check |
| `ops/prod-change-log.md` | **you** | Plan, backup, rollback path, verification |

All four belong in your submission.

## Constraints worth knowing

- Production records Alembic revision `0001_initial`. Migrations already
  applied to production must not be renamed or rewritten; add new ones.
- `./ops/prod-psql.sh --role app` opens production with writes enabled. Writes
  made that way bypass `prod-migrate.sh` and leave no change record.
- The application refuses to start against `slotwise_prod`, and the test suites
  refuse to run against it. That guard exists because the visible test fixture
  truncates every table.
- The database server is rebuilt empty if your workspace is rebuilt, so `ops/`
  keeps a checkpoint of production alongside the change log. Do not hand-edit
  it.
