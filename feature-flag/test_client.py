"""
test_client.py: public end-to-end smoke test
Run: python test_client.py

Uses Flask's local test client, so you do not need to start a separate server
process. This is a smoke test that also includes a few basic error
cases: it is NOT exhaustive.
"""

import sys

PASS = []
FAIL = []


def record(name, ok, details=""):
    if ok:
        PASS.append(name)
        print(f"PASS: {name}")
    else:
        FAIL.append(name)
        print(f"FAIL: {name} {details}")


def json_body(response):
    try:
        return response.get_json()
    except Exception:
        return None


def expect_json_error(name, response, status):
    data = json_body(response)
    ok = response.status_code == status and isinstance(data, dict) and set(data) == {"error"}
    record(name, ok, {"status": response.status_code, "body": data})


def sample_flag(**overrides):
    config = {
        "key": "new_checkout",
        "enabled": True,
        "variants": ["control", "treatment"],
        "default_variant": "control",
        "rules": [
            {
                "conditions": [
                    {"attribute": "country", "op": "in", "value": ["US", "CA"]},
                    {"attribute": "age", "op": "gt", "value": 18},
                ],
                "serve": "treatment",
            }
        ],
        "fallthrough": {"rollout": {"control": 50, "treatment": 50}},
    }
    config.update(overrides)
    return config


def main():
    import server

    client = server.app.test_client()

    print("\nA. Create and read")

    response = client.post("/flags", json=sample_flag())
    data = json_body(response)
    record(
        "POST /flags creates a flag (201)",
        response.status_code == 201
        and isinstance(data, dict)
        and data.get("key") == "new_checkout"
        and data.get("default_variant") == "control",
        data,
    )

    response = client.get("/flags/new_checkout")
    data = json_body(response)
    record(
        "GET /flags/<key> returns the config",
        response.status_code == 200
        and isinstance(data, dict)
        and data.get("variants") == ["control", "treatment"],
        data,
    )

    response = client.get("/flags")
    data = json_body(response)
    record(
        "GET /flags lists flags",
        response.status_code == 200
        and isinstance(data, list)
        and any(f.get("key") == "new_checkout" for f in data),
        data,
    )

    print("\nB. Evaluation")

    response = client.post(
        "/flags/new_checkout/evaluate",
        json={"user_id": "u1", "attributes": {"country": "US", "age": 30}},
    )
    data = json_body(response)
    record(
        "matching rule serves treatment",
        response.status_code == 200
        and data == {"value": "treatment", "reason": "RULE_MATCH", "rule_index": 0},
        data,
    )

    response = client.post(
        "/flags/new_checkout/evaluate",
        json={"user_id": "u1", "attributes": {"country": "FR", "age": 30}},
    )
    data = json_body(response)
    record(
        "no rule match falls through to a rollout variant",
        response.status_code == 200
        and isinstance(data, dict)
        and data.get("reason") == "FALLTHROUGH"
        and data.get("value") in ("control", "treatment"),
        data,
    )

    first = client.post(
        "/flags/new_checkout/evaluate", json={"user_id": "stable", "attributes": {}}
    )
    second = client.post(
        "/flags/new_checkout/evaluate", json={"user_id": "stable", "attributes": {}}
    )
    record(
        "fallthrough assignment is deterministic for the same user",
        first.status_code == 200
        and json_body(first) == json_body(second),
        {"first": json_body(first), "second": json_body(second)},
    )

    print("\nC. Update and disable")

    response = client.put("/flags/new_checkout", json=sample_flag(enabled=False))
    record("PUT /flags/<key> updates (200)", response.status_code == 200, json_body(response))

    response = client.post(
        "/flags/new_checkout/evaluate",
        json={"user_id": "u1", "attributes": {"country": "US", "age": 30}},
    )
    data = json_body(response)
    record(
        "disabled flag serves default_variant",
        response.status_code == 200
        and data == {"value": "control", "reason": "DISABLED"},
        data,
    )

    print("\nD. Delete")

    response = client.delete("/flags/new_checkout")
    record(
        "DELETE /flags/<key> (200)",
        response.status_code == 200 and json_body(response) == {"deleted": "new_checkout"},
        json_body(response),
    )
    expect_json_error("deleted flag is gone (404)", client.get("/flags/new_checkout"), 404)

    print("\nE. Basic error handling")

    client.post("/flags", json=sample_flag(key="dup"))
    expect_json_error(
        "duplicate key returns 409", client.post("/flags", json=sample_flag(key="dup")), 409
    )
    expect_json_error(
        "rollout not summing to 100 returns 400",
        client.post("/flags", json=sample_flag(key="bad", fallthrough={"rollout": {"control": 40, "treatment": 50}})),
        400,
    )
    expect_json_error(
        "evaluate missing flag returns 404",
        client.post("/flags/ghost/evaluate", json={"user_id": "u1"}),
        404,
    )
    expect_json_error(
        "evaluate without user_id returns 400",
        client.post("/flags/dup/evaluate", json={"attributes": {}}),
        400,
    )
    expect_json_error(
        "malformed JSON returns 400",
        client.post("/flags", data="{bad", content_type="application/json"),
        400,
    )
    expect_json_error(
        "unsupported method returns JSON 405", client.put("/flags", json=sample_flag()), 405
    )

    print("\n" + "=" * 60)
    print(f"Results: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("Failed checks:")
        for name in FAIL:
            print(f"  - {name}")
    print("=" * 60)

    sys.exit(0 if not FAIL else 1)


if __name__ == "__main__":
    main()
