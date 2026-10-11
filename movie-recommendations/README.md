
# NextFrame: personalized movie discovery

## What you should know

Mode: Debugging.

Use Python 3.12 with the standard library. The visible tests need no pip installation.

---

## Scenario

NextFrame returns empty or unhelpful recommendations even when a user has ratings and watch history. Repair its deterministic ranking pipeline and preserve the supplied endpoint.

---

## Files

Edit `service.py` and `REFLECTION.essay`. Keep the public names, signatures and supplied fixed files unchanged. You may add helper modules and your own regression tests.

---

## Public API

```text
RecommendationService(movies: list[dict], ratings: dict, history: dict)
recommend(user: str, limit: int = 10) -> list[dict]
```

Import the class from `service.py`. `models.ServiceError` exposes integer `status` and string `code`; `(status, code)` below refers to that exception, not a returned tuple, unless a success tuple is explicitly shown.

---

## Requirements

### 1. Catalogue and user data

- Constructor inputs are trusted catalogue data: movies have unique positive integer id, string title, `list[str]` genres (duplicates allowed), nonnegative integer popularity and boolean available.
- `ratings` maps user IDs to `{movie_id: integer rating 1..5}`; history maps users to lists of watched integer IDs.
- IDs in ratings/history can refer to removed movies.
- Copy nested inputs at construction.

### 2. Request validation

- `recommend` rejects non-integer/boolean limits or limits outside 1..50 with `ServiceError(400, "invalid_limit")`; then rejects a non-string or blank user with `(400, "invalid_user")`.
- Unknown nonblank users are valid cold-start users.

### 3. Candidate selection

- Exclude the union of this user's rated movie IDs and watched movie IDs.
- Also exclude unavailable movies.
- A rated movie is excluded regardless of its rating or presence in history.
- Only this user's data contributes preferences.

### 4. Genre weights and scores

- Each rating for a movie still in the catalogue contributes `rating - 3` to each distinct genre of that movie.
- Unavailable rated movies still contribute.
- Ignore orphan rating IDs when calculating weights.
- History alone supplies no weights.
- A candidate score is the sum of the resulting weights over its distinct genres.
- Scores may be negative or zero; do not discard such candidates.

### 5. Ordering and results

- Sort by score descending, popularity descending, then numeric id ascending.
- Return at most limit entries, or fewer if fewer are eligible.
- Each result has exactly `{id, title, score, popularity}`.
- Return `[]` when the catalogue is empty or all movies have been seen.
- For users without preferences, all scores are zero, so popularity and then id determine the order.
- Results must be detached; do not mutate source data or retain mutations made by the caller.

### 6. HTTP contract

- `GET /recommendations?limit=10` with `X-User-ID` returns 200 `{recommendations: [...]}`.
- The fixed adapter defaults limit to 10, parses integer query text, rejects malformed limits with `400 invalid_limit`, and returns `401 unauthorized` for missing/blank `X-User-ID`.
- ServiceError maps to `{error: code}`.
- Other routes return `404 not_found`; other methods return `405 method_not_allowed`.
- Run `python3 server.py` and use demo user alice.
- No external movie API or learning model is required.

---

## Implementation checklist

Each task is required.

1. Validate requests and handle empty inputs.
2. Exclude rated, watched and unavailable movies.
3. Calculate genre preferences from the user’s ratings.
4. Apply the ranking and tie-breaking rules, including for users without preferences.
5. Apply the result limit, return detached data and check the supplied endpoint.

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
