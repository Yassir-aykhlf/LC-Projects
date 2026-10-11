# Workspace commands

```bash
./scripts/run-local.sh        # start SlotWise on port 8080
./scripts/test-postgres.sh    # run the visible tests
./scripts/local-reset.sh      # wipe local and rebuild clean demo data
```

`run-local.sh` applies migrations to `slotwise_local`, seeds any missing demo
data, and serves both the JSON API and the observation UI from one process on
port 8080.

`test-postgres.sh` recreates the `public` schema in `slotwise_test`, applies
migrations, runs `tests/`, and writes JUnit evidence to
`artifacts/postgres-visible.xml`. It rebuilds the schema at the *start* of a
run, so a failing run leaves its data in place for you to inspect. Your
submitted tests are re-run with this script exactly as it ships.

`local-reset.sh` only ever touches `slotwise_local`.

Two supporting files you do not normally run yourself:

- `_env.sh` — the single source of environment truth. Every script here sources
  it, and so does each new terminal.
- `db-bootstrap.sh` — initializes data in the databases pre-created by the
  sandbox service. It uses only ordinary database-owner roles, is idempotent,
  and is re-run automatically whenever the workspace starts.

PostgreSQL runs beside this workspace and is not started from here. If your
Python environment or one of the databases ever looks missing, run **Re-run
initialization** from the IDE's quick actions to prepare the workspace again.

All of these work against the **local** and **test** databases. Production is
reached only through `./ops/`; see [`../ops/README.md`](../ops/README.md).
