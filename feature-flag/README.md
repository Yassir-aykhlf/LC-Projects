
# Feature flag and experiment assignment service

## What you should know

Before you begin, make sure you understand:

- HTTP APIs and status codes
- Hashing and deterministic assignment
- Basic concurrency and locking

## Scenario

You are building the backend for a **feature-flag and experiment-assignment service** used
by product teams to roll features out gradually and to run A/B experiments.

A *flag* defines a set of named **variants** (for a simple on/off feature that might be
`["off", "on"]`; for an experiment, `["control", "treatment"]`). When the service evaluates
a flag for a given user, it decides **which variant that user should see** by applying, in
order:

1. an **enabled** switch,
2. a list of ordered **targeting rules** that match on user attributes, and
3. a **deterministic percentage rollout** for everyone the rules don't capture.

The HTTP server is already implemented and **must not be modified**. Your task is to
implement the `FeatureFlagService` class in `feature_flags.py`, which stores flag
configuration in memory and evaluates it. The server calls your service to create, read,
update, delete, and evaluate flags.

The focus is correct evaluation semantics: ordered rule matching, deterministic bucketing,
configuration consistency across updates, and safety under concurrent requests.

---

## Goal

Implement an in-memory feature-flag service that supports:

- creating, reading, updating, deleting, and listing flags,
- validating flag configuration,
- evaluating a flag for a user via ordered rules and a deterministic percentage rollout,
- returning dictionaries that match the contract below and are safe to mutate,
- behaving correctly under concurrent requests.

---

## Files

You are given:

- `server.py`: completed HTTP server, **do not modify**
- `feature_flags.py`: your implementation file
- `test_client.py`: public smoke test
- `REFLECTION.essay`: graded design-reflection questions
- `requirements.txt`: local dependencies
- `README.md`: this file

For the required implementation, edit:

- `feature_flags.py`
- `REFLECTION.essay`

Write your reflection answers in `REFLECTION.essay`. Graders will not look for answers in
code comments or other files.

---

## The flag configuration

A flag is a JSON object. Here is a complete example:

```json
{
  "key": "checkout_flow",
  "enabled": true,
  "variants": ["control", "treatment"],
  "default_variant": "control",
  "rules": [
    {
      "conditions": [
        {"attribute": "country", "op": "in", "value": ["US", "CA"]},
        {"attribute": "age", "op": "gt", "value": 18}
      ],
      "serve": "treatment"
    }
  ],
  "fallthrough": { "rollout": { "control": 80, "treatment": 20 } }
}
```

| Field | Meaning |
|-------|---------|
| `key` | Unique flag identifier. Must match `^[A-Za-z0-9_-]{1,64}$`. |
| `enabled` | Boolean. When `false`, evaluation returns `default_variant` and stops. |
| `variants` | Non-empty list of unique, non-empty strings: the full set of values the flag can serve. |
| `default_variant` | Must be one of `variants`. Served when the flag is **disabled**. |
| `rules` | Optional ordered list of targeting rules. It defaults to `[]`. Rules are evaluated top to bottom; **the first matching rule wins**. |
| `fallthrough.rollout` | **Required.** A non-empty map from variant name to integer percent, applied to users who match no rule. Keys must be a subset of `variants`; omitted variants have zero weight. Values are non-negative integers that **sum to exactly 100**. |

### Rule

```json
{ "conditions": [ ... ], "serve": "treatment" }
```

- `conditions`: an optional list of conditions combined with **AND**. It defaults to `[]`.
  A rule matches only if **all** of its conditions match, and an empty list matches every
  user.
- `serve`: the variant served when the rule matches; must be one of `variants`.

### Condition

```json
{ "attribute": "country", "op": "in", "value": ["US", "CA"] }
```

A condition reads `attributes[attribute]` from the evaluation request and compares it to
`value` using `op`:

| `op` | Matches when | `value` type |
|------|--------------|--------------|
| `eq` | attribute equals `value` | string, number, or boolean |
| `neq` | attribute does not equal `value` | string, number, or boolean |
| `in` | attribute is a member of `value` | list |
| `not_in` | attribute is not a member of `value` | list |
| `gt` | attribute is a number greater than `value` | number |
| `lt` | attribute is a number less than `value` | number |
| `contains` | attribute is a string that contains the substring `value` | string |

**Attribute handling during evaluation:** if the attribute is **missing** from the request,
or its type does not fit the operator (for example `gt`/`lt` on a non-number, or `contains`
on a non-string), the condition simply **evaluates to false**: it never raises. For `gt`
and `lt`, a boolean is **not** treated as a number.

---

## Evaluation

```text
evaluate(flag_key, user_id, attributes) -> result
```

The service first validates `user_id` and `attributes`. It then resolves a variant in this
order:

1. If the flag does not exist → raise `NotFoundError`.
2. If the flag is **disabled** → return `default_variant` with reason `DISABLED`.
3. Otherwise walk `rules` in order. For the **first** rule whose conditions **all** match →
   return that rule's `serve` with reason `RULE_MATCH` and the matched `rule_index`.
4. If no rule matches → apply the **fallthrough rollout** (see below) and return the bucketed
   variant with reason `FALLTHROUGH`.

`default_variant` is only used for the disabled case. An enabled flag always resolves through
rules and then the fallthrough rollout.

### Result shape

```json
{ "value": "treatment", "reason": "RULE_MATCH", "rule_index": 0 }
```

- `value`: the served variant (always one of the flag's `variants`).
- `reason`: one of `"DISABLED"`, `"RULE_MATCH"`, `"FALLTHROUGH"`.
- `rule_index`: included **only** when `reason` is `"RULE_MATCH"` (the 0-based index of the
  matched rule). It must **not** be present for the other reasons.

---

## Deterministic rollout bucketing

Percentage rollout must be **deterministic**: the same `(flag_key, user_id)` pair must always
resolve to the same variant. **Do not use random number generation.** Use exactly this
formula so your assignments are reproducible:

```text
from hashlib import sha256

bucket = int(sha256(f"{flag_key}:{user_id}".encode("utf-8")).hexdigest(), 16) % 10000
# bucket is in 0 .. 9999
```

That gives each user a stable integer in `[0, 10000)` (a percentage with two decimal
places). Variants then claim **cumulative ranges in the order they appear in the flag's
`variants` list** (not the order of keys in the rollout map). Each percentage point of
rollout is worth 100 bucket units, so weights that sum to 100 tile `[0, 10000)` with no gaps:

```text
variants ["control", "treatment"], rollout { "control": 80, "treatment": 20 }:

  control:    bucket in [0,    8000)
  treatment:  bucket in [8000, 10000)

The chosen variant is the one whose range contains the user's bucket.
```

**Worked example** (flag `checkout_flow`, rollout `control: 80 / treatment: 20`):

| `user_id` | `bucket` | variant |
|-----------|----------|---------|
| `user-1` | `6526` | `control` (in `[0, 8000)`) |
| `user-42` | `9594` | `treatment` (in `[8000, 10000)`) |

Because the bucket depends only on `(flag_key, user_id)`, changing the percentages moves
range boundaries without rehashing users. For example, changing an ordered rollout from
`control: 80 / treatment: 20` to `control: 70 / treatment: 30` adds users to `treatment`
without removing anyone who was already assigned to it.

---

## Service interface

The server calls these methods on your `FeatureFlagService`. Preserve their names and the
exception classes.

```python
create_flag(config: dict) -> dict        # raise ConflictError if the key already exists
get_flag(key: str) -> dict | None         # None if the flag does not exist
update_flag(key: str, config: dict) -> dict   # raise NotFoundError if it does not exist
delete_flag(key: str) -> bool             # True if it existed, False otherwise
list_flags() -> list[dict]
evaluate(key: str, user_id: str, attributes: dict | None = None) -> dict
```

Exceptions live in `feature_flags.py` and are mapped to HTTP status codes by the server:

| Exception | HTTP status |
|-----------|-------------|
| `ValidationError` | `400 Bad Request` |
| `NotFoundError` | `404 Not Found` |
| `ConflictError` | `409 Conflict` |

(`FeatureFlagError` is their shared base class.) Exact exception messages are **not** part of
the contract.

---

## HTTP API

The server (fixed) exposes the following. Every API and routing error listed below is a JSON
object of exactly the shape `{ "error": "..." }`.

| Method & path | Request body | Success | Errors |
|---------------|--------------|---------|--------|
| `POST /flags` | flag config | `201` + stored config | `400` invalid, `409` key exists |
| `GET /flags` | none | `200` + list of configs | none |
| `GET /flags/<key>` | none | `200` + config | `404` |
| `PUT /flags/<key>` | full flag config (replaces) | `200` + config | `400`, `404` |
| `DELETE /flags/<key>` | none | `200` `{"deleted": <key>}` | `404` |
| `POST /flags/<key>/evaluate` | `{"user_id": "...", "attributes": {...}}` | `200` + result | `400`, `404` |

Notes:

- `PUT` is a **full replacement** of the flag's configuration. The `key` in the body must
  match the `<key>` in the path.
- For `evaluate`, `user_id` is required and must be a non-empty string; `attributes` is
  optional and defaults to `{}`.

---

## Validation

`create_flag` and `update_flag` must raise `ValidationError` when the config is invalid,
including:

- `key` missing or not matching `^[A-Za-z0-9_-]{1,64}$`
- `enabled` not a boolean
- `variants` not a non-empty list of unique, non-empty strings
- `default_variant` not one of `variants`
- `rules` not a list, a rule not an object, or `conditions` not a list
- any rule's `serve` not one of `variants`
- a condition with an empty or non-string `attribute`, an unknown `op`, or a `value` whose
  type does not fit the operator (`in`/`not_in` need a list; `gt`/`lt` need a number;
  `contains` needs a string)
- `fallthrough` not an object, or `fallthrough.rollout` missing or empty
- rollout keys that are not declared variants, non-integer or negative weights, or weights
  that do not sum to exactly 100

The service normalizes accepted configurations before storing them. It drops extra
properties from the flag, rule, condition, and `fallthrough` objects. Every key inside the
rollout map must still name a declared variant.

`evaluate` must raise `ValidationError` if `user_id` is not a non-empty string, or if
`attributes` is provided but is not an object.

---

## Requirements

### Required

You must:

- implement all six `FeatureFlagService` methods
- create, read, update, delete, and list flags, validating configuration as described above
- reject a duplicate `key` (`ConflictError`) and operate on a missing flag with
  `NotFoundError`
- evaluate flags with **ordered, first-match-wins** rules and **AND-combined** conditions,
  supporting all seven operators
- return `default_variant` (reason `DISABLED`) for a disabled flag
- compute the **fallthrough rollout deterministically** using the pinned formula
- return exactly the documented result and config shapes, and return dictionaries that are
  **safe for callers to mutate** without corrupting stored state
- be **safe under concurrent** create / update / delete / evaluate calls

### Extended

Stronger solutions will also:

- keep evaluation **consistent across updates**: after `update_flag`, evaluations reflect the
  new configuration atomically (never a half-applied flag)
- validate every malformed-config case cleanly rather than crashing
- handle missing or wrongly-typed attributes during evaluation as a clean non-match
- keep the service cohesive: raise the right exception types and keep HTTP concerns out of
  `feature_flags.py`

### Reflection

Answer questions in `REFLECTION.essay` to demonstrate your systems reasoning and engineering judgment:

- why bucketing uses `(flag_key, user_id)` but not the rollout percentages
- how evaluation avoids seeing a partially applied update
- how you would share configuration across multiple service instances without changing
  user assignments

The prompts are already in `REFLECTION.essay`; write each answer in its question's answer
field. These answers are graded separately from the automated correctness tests.

---

## Estimated completion time

60 minutes

---

## Running locally

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run the public smoke test (uses Flask's local test client: no separate server needed):

```bash
python3 test_client.py
```

To try the API manually, start the server:

```bash
python3 server.py
```

Then send requests to `http://127.0.0.1:8080`, for example:

```bash
# Create a flag
curl -X POST http://127.0.0.1:8080/flags \
  -H 'Content-Type: application/json' \
  -d '{
        "key": "checkout_flow",
        "enabled": true,
        "variants": ["control", "treatment"],
        "default_variant": "control",
        "rules": [],
        "fallthrough": {"rollout": {"control": 80, "treatment": 20}}
      }'

# Evaluate it for a user
curl -X POST http://127.0.0.1:8080/flags/checkout_flow/evaluate \
  -H 'Content-Type: application/json' \
  -d '{"user_id": "user-42", "attributes": {}}'
```

> The public smoke test is not exhaustive. Hidden tests check additional edge cases: the full
> validation matrix, deterministic bucketing and rollout stickiness, rule precedence, exact
> response shapes, mutation safety, and concurrency.
