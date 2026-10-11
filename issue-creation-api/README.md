
# IssueHub: authorized and retry-safe issue creation

## What you should know

Mode: Completion.

Use Python 3.12 with the standard library. The visible tests need no pip installation.

---

## Scenario

IssueHub needs a project issue API that remains correct when clients retry creation and teammates update issues concurrently. Complete the service behind the supplied HTTP adapter.

---

## Files

Edit `service.py` and `REFLECTION.essay`. Keep the public names, signatures and supplied fixed files unchanged. You may add helper modules and your own regression tests.

---

## Public API

```text
IssueService(members: dict[str, iterable[str]])
create(user, project, payload, key=None) -> (status, dict)
get(user, project, issue_id) -> dict
transition(user, project, issue_id, status, version) -> dict
list(user, project, status=None, after_id=0, limit=20) -> list[dict]
```

Import the class from `service.py`. `models.ServiceError` exposes integer `status` and string `code`; `(status, code)` below refers to that exception, not a returned tuple, unless a success tuple is explicitly shown.

---

## Requirements

### 1. Membership and authorization

- `members` supplies valid project IDs and user memberships.
- Copy this data at construction so later changes to the input cannot affect authorization.
- Every method authorizes before its own validation: missing/non-string/blank user -> `ServiceError(401, "unauthorized")`; unknown project or nonmember -> `(404, "project_not_found")`.
- Project members can read and update each other's issues.
- State is in memory for one service instance; disk persistence is not required.

### 2. Creation input

- `create` payload is a dict with required title and optional description, no extra fields.
- `title` must be a string, stripped length 1..120; store stripped title.
- `description` defaults to `""`, must be a string of at most 2000 characters and is preserved exactly.
- `key` is `None` or a string of length 1..64 (whitespace is significant).
- Invalid inputs -> `(400, "invalid_input")`.

### 3. Creation and retrieval

- Creation returns `(201, {id, project, creator: user, title, description, status: "open", version: 1})`.
- IDs start at 1 and increase globally across the instance.
- Failed creates and replays do not consume IDs.
- Without a key, every successful request creates a new issue.
- `get` returns a detached current issue; missing IDs or IDs under another project raise `(404, "issue_not_found")`.

### 4. Idempotency

- Idempotency scope is (user, project, key).
- Reusing a key with the same stripped title and exact/defaulted description returns (200, the current issue), even after status changes.
- A different canonical payload raises `(409, "idempotency_conflict")`.
- Different users/projects may reuse a key independently.
- Concurrent identical creates with the same scope produce exactly one 201 and one saved issue; all others return 200.

### 5. Status changes and versions

- `transition` authorizes and looks up the issue, then validates status in `{"open","closed"}` and positive non-boolean integer version.
- Invalid values -> `(400, "invalid_input")`.
- `version` must match the current version, even for a same-status request; otherwise `(409, "version_conflict")`.
- A changed status increments version once; a same-status request leaves version unchanged.
- Both transitions `open->closed` and `closed->open` are allowed.
- Concurrent writes at one version can change the status only once.

### 6. Listing and concurrency

- `list` validates status as `None`/open/closed, `after_id` as nonnegative non-boolean integer, and limit as non-boolean integer 1..100.
- Invalid inputs -> `(400, "invalid_input")`.
- Return only the project's matching issues with id strictly greater than `after_id`, ordered by id ascending, then limited.
- All inputs/results are isolated; failed operations are atomic, and all methods are safe for same-instance concurrency.

### 7. HTTP contract

- HTTP: `POST/GET /projects/{project}/issues`; `GET/PATCH /projects/{project}/issues/{id}`.
- `X-User-ID` provides identity.
- POST accepts the creation payload and optional `Idempotency-Key` header.
- GET collection supports status, `after_id` and limit query parameters.
- PATCH body is exactly `{status, version}`.
- GET/PATCH success is 200.
- Errors are `{error: code}`; the fixed adapter rejects malformed JSON with `400 invalid_json`, malformed query integers or wrong PATCH fields with `400 invalid_input`, unknown routes with `404 not_found`, and unsupported methods with `405 method_not_allowed`.
- Demo project demo has alice and bob.

---

## Implementation checklist

Each task is required.

1. Authorize each request before validating its inputs.
2. Create issues and retain their state for later requests.
3. Handle creation retries within the user, project and key scope.
4. Check versions when changing issue status.
5. Filter and paginate issue lists, then exercise the service through the supplied HTTP adapter.

---

## Estimated completion time

75 minutes, including investigation, implementation, regression testing and the reflection answers.

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
