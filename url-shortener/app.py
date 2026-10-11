"""
app.py — candidate implementation file

Complete the Flask routes for the URL shortener API. The service logic belongs
in shortener.py; the route layer should parse requests, call URLShortener, and
map service outcomes to the required HTTP responses.
"""

from flask import Flask, jsonify, redirect, request

from shortener import (
    CodeGenerationError,
    ConflictError,
    ExpiredLinkError,
    NotFoundError,
    PermissionDeniedError,
    URLShortener,
    ValidationError,
)

app = Flask(__name__)
app.url_map.strict_slashes = False
svc = URLShortener()


def error(message: str, status: int):
    return jsonify({"error": message}), status


def short_url_for(short_code: str) -> str:
    return request.host_url.rstrip("/") + "/" + short_code


@app.post("/links")
def create_link():
    """
    Create a short link.

    JSON body:
      long_url: required string starting with http:// or https://
      custom_code: optional [A-Za-z0-9_-]{3,32}
      ttl_seconds: optional positive number

    Success: 201 with link metadata, short_url, and owner_token.
    """
    raise NotImplementedError


@app.get("/<short_code>")
def redirect_link(short_code: str):
    """
    Redirect to the original URL.

    Success: 302 with Location header.
    Missing code: 404.
    Expired code: 410.
    A successful redirect must atomically increment hit_count exactly once.
    """
    raise NotImplementedError


@app.get("/links/<short_code>")
def get_link(short_code: str):
    """Return metadata for a short link, or 404 when it does not exist."""
    raise NotImplementedError


@app.delete("/links/<short_code>")
def delete_link(short_code: str):
    """
    Delete a short link.

    JSON body must contain owner_token.
    Missing token: 400.
    Wrong token: 403.
    Missing code: 404.
    Success: 200 with {"deleted": short_code}.
    """
    raise NotImplementedError


@app.get("/stats")
def stats():
    """Return aggregate statistics across non-deleted links."""
    raise NotImplementedError


@app.errorhandler(400)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(409)
@app.errorhandler(410)
@app.errorhandler(405)
def handle_http_error(exc):
    return error(getattr(exc, "description", "request failed"), exc.code)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True, threaded=True)
