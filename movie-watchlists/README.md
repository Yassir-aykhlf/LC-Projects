
# ScreenShelf: persistent private watchlists

## What you should know

Mode: Debugging.

Use Python 3.12 with the standard library. The visible tests need no pip installation.

---

## Scenario

ScreenShelf users see duplicate-add status errors, movies removed from the wrong list, and changes missing after reconnecting. Repair the SQLite-backed service; the HTTP adapter is supplied.

---

## Files

Edit `service.py` and `REFLECTION.essay`. Keep the public names, signatures and supplied fixed files unchanged. You may add helper modules and your own regression tests.

---

## Public API

```text
WatchlistService(database_path: str)
create(user, name) -> (status, dict)
get(user, list_id) -> dict
rename(user, list_id, name) -> (status, dict)
delete(user, list_id) -> (204, None)
add_movie(user, list_id, movie_id) -> (status, dict)
remove_movie(user, list_id, movie_id) -> (204, None)
close() -> None
```

Import the class from `service.py`. `models.ServiceError` exposes integer `status` and string `code`; `(status, code)` below refers to that exception, not a returned tuple, unless a success tuple is explicitly shown.

---

## Requirements

### 1. Names and identifiers

- The service is given valid nonblank string user IDs by the adapter.
- Names must be strings with 1..80 Unicode characters after `strip()`; store the stripped name.
- Invalid names raise `ServiceError(400, "invalid_name")`.
- Movie IDs must be non-boolean positive integers no larger than 2147483647; invalid IDs raise `(400, "invalid_movie")`.
- Movies need not exist in a catalogue.
- List IDs supplied to service methods are positive signed-64-bit integers.
- The adapter returns `404 not_found` for list IDs outside that range.

### 2. Create, retrieve and rename

- `create` returns `(201, {id, owner: user, name, movies: []})`.
- SQLite-generated IDs are positive, never reused after successful deletion, and fresh databases start at 1.
- Duplicate names are allowed.
- `get` returns that shape with unique movie IDs sorted ascending.
- `rename` returns (200, updated list).
- All returned data is detached.

### 3. Ownership and validation order

- A list belongs to exactly one user.
- For get, rename, delete, `add_movie` and `remove_movie`, missing lists and another user's lists both raise `(404, "list_not_found")`.
- Validate a new name or movie ID before checking list ownership.
- Rejected operations leave data unchanged.

### 4. Movie membership and deletion

- `add_movie` inserts once and returns (201, updated list); adding an existing movie returns (200, unchanged list).
- Membership is scoped to one list.
- `remove_movie` removes only the specified movie and returns `(204, None)`; absent membership raises `(404, "movie_not_found")`.
- `delete` removes only the requested list and its memberships, returns `(204, None)`; repeating deletion raises `list_not_found`.

### 5. Persistence and connections

- Writes must be committed before returning.
- Reopening the same SQLite path, including through a second service instance, sees saved names, additions, removals and deletions.
- Separate database paths isolate data.
- `close` releases the connection.
- Single-instance calls are serialized safely; high-contention multi-process SQLite tuning is discussion-only.
- Do not replace persistence with process-global memory.

### 6. HTTP contract

- HTTP: `POST /watchlists` `{name}`; `GET/PATCH/DELETE /watchlists/{id}` (PATCH body `{name}`); `POST /watchlists/{id}/movies` `{movie_id}`; `DELETE /watchlists/{id}/movies/{movie_id}`.
- `X-User-ID` is required; missing/blank -> `401 unauthorized`.
- Errors are `{error: code}`.
- GET succeeds with 200; service write statuses carry through, and 204 has no response body.
- The fixed adapter handles malformed JSON (`400 invalid_json`), malformed routes (`404 not_found`), unsupported methods (`405 method_not_allowed`), and unexpected body keys (`400 invalid_input`).

---

## Implementation checklist

Each task is required.

1. Validate and save watchlist names.
2. Allow users to access only their own lists.
3. Add movies and distinguish a new addition from a duplicate.
4. Remove only the requested movie from the requested list.
5. Delete lists with their entries and preserve committed changes across connections.

---

## Estimated completion time

60 minutes, including investigation, implementation, regression testing and the reflection answers.

---

## Running locally

```bash
bash .theia/run_tests.sh
# Equivalent:
python3 -B test_client.py
```

Some tests will fail against the starter code. After making changes, check the test results as well as whether the process starts. The visible tests cover part of the contract; your implementation must satisfy all the rules above. Tests have time limits and use temporary state.

After completing the code, fill in each question’s `answer` field in `REFLECTION.essay`. The questions ask you to explain your approach and discuss possible future changes. You do not need to implement the proposed extensions.

### Try the endpoint

```bash
python3 server.py
```

Use the documented routes at `http://127.0.0.1:8080` and the `X-User-ID` header. The adapter is already complete.
