
# ContentGate: keyword and user blocklists

## What you should know

Mode: Completion.

Use Python 3.12 with the standard library. The visible tests need no pip installation.

---

## Scenario

ContentGate is a request admission component for a discussion service. Implement configurable keyword matching, manual user blocks and automatic blocking after repeated violations. This is separate from request-rate limiting.

---

## Files

Edit `service.py` and `REFLECTION.essay`. Keep the public names, signatures and supplied fixed files unchanged. You may add helper modules and your own regression tests.

---

## Public API

```text
BlocklistService(keywords=(), blocked_users=())
replace_keywords(keywords: iterable[str]) -> None
replace_blocked_users(users: iterable[str]) -> None
state(user: str) -> dict
check(user: str, content: str) -> dict
```

Import the class from `service.py`. `models.ServiceError` exposes integer `status` and string `code`; `(status, code)` below refers to that exception, not a returned tuple, unless a success tuple is explicitly shown.

---

## Requirements

### 1. Configuration validation

- Configuration inputs are finite iterables of strings.
- Reject a bare string/bytes iterable and any non-string or blank entry with `ServiceError(400, "invalid_keywords")` or `(400, "invalid_users")`.
- Validate all entries before replacing anything, including in the constructor.
- Snapshot input data; one-pass iterables are supported.

### 2. Keyword matching

- Normalize keywords with `strip().casefold()`, then deduplicate.
- Normalize content only with `casefold()`.
- Matching is literal substring matching, not regex or word-token matching.
- Each normalized keyword appears at most once in matches, sorted by Python string order.
- Overlapping keywords both match.
- Empty content is valid and matches nothing.
- No Unicode normalization beyond casefold is required.

### 3. User validation and state

- User IDs are case-sensitive and preserved exactly, including surrounding whitespace.
- `check` rejects non-string/blank users or non-string content with `(400, "invalid_input")` before doing any matching or accounting.
- `state` is called with a valid user and returns `{strikes: int, blocked: bool}`; unknown users have zero strikes.

### 4. Blocked users

- A user is blocked if present in the manual set or their strike count is at least 3.
- For a blocked user, check returns exactly `{allowed: False, reason: "user_blocked", matches: [], strikes: current_count}` without matching content or increasing strikes.
- This takes precedence over keyword rejection.

### 5. Violations and strikes

- For an unblocked user, any keyword match rejects with `{allowed: False, reason: "keyword", matches: sorted_matches, strikes: previous+1}`.
- Each rejected request adds exactly one strike, regardless of how many matches or occurrences it contains.
- The third rejection still has `reason="keyword"`; later calls are `user_blocked`.
- A clean request returns `{allowed: True, reason: None, matches: [], strikes: current_count}`, without resetting strikes.

### 6. Configuration updates and isolation

- `replace_keywords` and `replace_blocked_users` replace their respective entire sets; empty iterables clear them.
- Removing a manual block unblocks a user only if `strikes < 3`.
- Neither replacement clears strikes or automatically blocked users.
- State is retained in the instance, and all calls/replacements are atomic and safe under concurrent use.
- Invalid replacements leave previous configuration intact.
- Instances and returned snapshots are isolated.
- No HTTP server, disk storage or timed expiry is required.

---

## Implementation checklist

Each task is required.

1. Validate configuration and normalize keywords.
2. Find every matching keyword using the documented substring rules.
3. Enforce both manual blocks and blocks caused by repeated violations.
4. Add one strike per request rejected for a keyword match, including under concurrent calls.
5. Replace configuration atomically and keep instances and returned data isolated.

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
