
# ReviewDesk: moderation and permanent strikes

## What you should know

Mode: Debugging.

Use Python 3.12 with the standard library. The visible tests need no pip installation.

---

## Scenario

ReviewDesk accepts product reviews through a supplied content checker. Reports suggest edits bypass moderation and repeat violators continue posting. Repair creation, editing, strike persistence and failure handling.

---

## Files

Edit `service.py` and `REFLECTION.essay`. Keep the public names, signatures and supplied fixed files unchanged. You may add helper modules and your own regression tests.

---

## Public API

```text
ReviewService(checker: Callable[[str], bool])
create(user: str, content: str) -> dict
edit(review_id: int, user: str, content: str) -> dict
get(review_id: int) -> dict
user_state(user: str) -> dict
```

Import the class from `service.py`. `models.ServiceError` exposes integer `status` and string `code`; `(status, code)` below refers to that exception, not a returned tuple, unless a success tuple is explicitly shown.

---

## Requirements

### 1. Input validation and checker

- User IDs (including the `user_state` argument) and content must be nonempty, non-whitespace strings; invalid values raise `ServiceError(400, "invalid_input")`.
- Preserve the original content and user ID, including surrounding whitespace.
- The checker receives the exact content once for each authorized, valid, unblocked write.
- It returns a boolean: `True` permits, `False` rejects.

### 2. Creation and retrieval

- A successful create returns `{id, user, content, version: 1}`, with monotonically increasing integer IDs from 1, and saves it.
- Rejected writes do not consume IDs.
- A missing get raises `(404, "review_not_found")`.
- `get` and write results are detached snapshots.

### 3. Rejected content and strikes

- A checker rejection raises `(422, "content_rejected")`, increments that user's permanent strike count by exactly one and saves no new content.
- Rejected edits preserve existing content and version.
- Successful writes never reset strikes.
- `user_state` returns exactly `{strikes: int, flagged: bool}`; unknown users start at zero/`False`.

### 4. Blocking after three strikes

- The third rejected write still returns `content_rejected` and leaves `strikes=3`, `flagged=True`.
- Every subsequent valid write by that user raises `(403, "user_blocked")` without calling the checker or adding strikes, even if the content is clean.
- No unflag/reset operation exists.
- State lasts for the instance lifetime.

### 5. Write validation order

- `create` validates input, checks the flag, then invokes the checker.
- `edit` validates input, checks review existence, then ownership, then flag, then checker.
- Missing review -> `(404, "review_not_found")`; another owner -> `(403, "forbidden")`.
- A successful edit preserves id/user and increments version by one, including identical-content edits.

### 6. Checker failures and concurrency

- If the checker raises `Exception`, return `(503, "checker_unavailable")` without modifying reviews, strikes or IDs.
- Do not catch `BaseException`.
- Same-instance concurrent calls must be safe, including concurrent third-strike attempts.
- Different instances and users are isolated.
- No durable database or external checker implementation is required.

---

## Implementation checklist

Each task is required.

1. Pass the original content to the checker and save reviews only when permitted.
2. Keep each user’s strike count across creates and edits.
3. Block further writes after the third rejection.
4. Check ownership before editing and update the saved content and version on success.
5. Handle checker failures without changing reviews, strikes or ID allocation.

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
