
# ReturnGuard: deterministic return risk

## What you should know

Mode: Debugging.

Use Python 3.12 with the standard library. The visible tests need no pip installation.

---

## Scenario

A return-eligibility team sees inconsistent decisions at policy boundaries. Repair the deterministic scoring engine and its batch method. The policy below is fictional and complete; no external business rules apply.

---

## Files

Edit `service.py` and `REFLECTION.essay`. Keep the public names, signatures and supplied fixed files unchanged. You may add helper modules and your own regression tests.

---

## Public API

```text
RiskEngine()
evaluate(rating, value_cents, account_age_days) -> dict
evaluate_many(records: iterable[dict]) -> list[dict]
```

Import the class from `service.py`. `models.ServiceError` exposes integer `status` and string `code`; `(status, code)` below refers to that exception, not a returned tuple, unless a success tuple is explicitly shown.

---

## Requirements

### 1. Input validation

- `evaluate` accepts integer rating 1..5, nonnegative integer `value_cents` and nonnegative integer `account_age_days`.
- Reject booleans, floats, strings, missing values passed as `None`, and out-of-range values with `ServiceError(400, "invalid_input")`.
- Valid integers have no artificial upper bound except the rating range.

### 2. Component points

- Rating points: 1 -> 40, 2 -> 30, 3 -> 20, 4 -> 10, 5 -> 0.
- Value points: 0..9999 cents -> 0; 10000..49999 -> 15; >= 50000 -> 30.
- Age points: 0..29 days -> 25; 30..179 -> 10; >= 180 -> 0.

### 3. Score and decision

- The score is the sum of the three components, with no normalization, rounding or clamping.
- Scores < 30 approve; `30 <= score < 60` require `manual_review`; `score >= 60` rejects.
- Return exactly `{score: int, decision: "approve" | "manual_review" | "reject", components: {rating: int, value: int, age: int}}`.

### 4. Batch evaluation

- `evaluate_many` consumes a finite iterable once and returns one result in input order for each item.
- Each item must be a dictionary with exactly rating, `value_cents`, `account_age_days`.
- Valid items produce `{result: evaluate(...), error: None}`; invalid items produce `{result: None, error: "invalid_input"}`.
- A bad item must not stop later items.
- Empty input returns `[]`.
- Do not catch unrelated exceptions raised by the input iterator.

### 5. Stateless behavior

- The engine is stateless.
- Calls and returned nested dictionaries must not affect other results or mutate inputs.
- There are no wall-clock, network, currency conversion, or learned-model dependencies.

---

## Implementation checklist

Each task is required.

1. Check input types and ranges before calculating a score.
2. Apply the rating and account-age points from the policy.
3. Calculate value points at every threshold, including the exact boundary values.
4. Map the total score to the correct decision.
5. Keep batch results in input order and handle invalid records without stopping the batch.

---

## Estimated completion time

45 minutes, including investigation, implementation, regression testing and the reflection answers.

---

## Running locally

```bash
bash .theia/run_tests.sh
# Equivalent:
python3 -B test_client.py
```

Some tests will fail against the starter code. After making changes, check the test results as well as whether the process starts. The visible tests cover part of the contract; your implementation must satisfy all the rules above. Tests have time limits and use temporary state.

After completing the code, fill in each question’s `answer` field in `REFLECTION.essay`. The questions ask you to explain your approach and discuss possible future changes. You do not need to implement the proposed extensions.
