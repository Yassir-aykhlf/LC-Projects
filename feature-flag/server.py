"""
server.py: fixed HTTP boundary. Do NOT modify this file.

Implement FeatureFlagService in feature_flags.py. This module wires the service
to the HTTP API, parses request bodies, and maps service exceptions to status
codes. Every error response is a JSON object of the exact shape {"error": "..."}.
"""

from flask import Flask, jsonify, request

from feature_flags import (
    ConflictError,
    FeatureFlagService,
    NotFoundError,
    ValidationError,
)

app = Flask(__name__)
app.url_map.strict_slashes = False
service = FeatureFlagService()


def error(message: str, status: int):
    return jsonify({"error": message}), status


def parse_json_object() -> dict:
    """Return the request body as a JSON object, or raise ValidationError."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError("request body must be a JSON object")
    return data


@app.post("/flags")
def create_flag():
    try:
        config = parse_json_object()
        return jsonify(service.create_flag(config)), 201
    except ValidationError as exc:
        return error(str(exc), 400)
    except ConflictError as exc:
        return error(str(exc), 409)


@app.get("/flags")
def list_flags():
    return jsonify(service.list_flags()), 200


@app.get("/flags/<key>")
def get_flag(key: str):
    flag = service.get_flag(key)
    if flag is None:
        return error("flag not found", 404)
    return jsonify(flag), 200


@app.put("/flags/<key>")
def update_flag(key: str):
    try:
        config = parse_json_object()
        return jsonify(service.update_flag(key, config)), 200
    except ValidationError as exc:
        return error(str(exc), 400)
    except NotFoundError as exc:
        return error(str(exc), 404)


@app.delete("/flags/<key>")
def delete_flag(key: str):
    if service.delete_flag(key):
        return jsonify({"deleted": key}), 200
    return error("flag not found", 404)


@app.post("/flags/<key>/evaluate")
def evaluate_flag(key: str):
    try:
        body = parse_json_object()
        result = service.evaluate(key, body.get("user_id"), body.get("attributes", {}))
        return jsonify(result), 200
    except ValidationError as exc:
        return error(str(exc), 400)
    except NotFoundError as exc:
        return error(str(exc), 404)


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_http_error(exc):
    return error(getattr(exc, "description", "request failed"), exc.code)


if __name__ == "__main__":
    print("Feature Flag service listening on http://127.0.0.1:8080")
    app.run(host="127.0.0.1", port=8080, debug=True, threaded=True)
