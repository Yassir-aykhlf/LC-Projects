"""
Candidate implementation file.

Complete the FeatureFlagService used by server.py. You may add helper methods,
classes, and constants, but preserve the public method names and the exception
classes used by server.py and the tests:

    create_flag(config)            -> dict        (ConflictError if key exists)
    get_flag(key)                  -> dict | None
    update_flag(key, config)       -> dict        (NotFoundError if absent)
    delete_flag(key)               -> bool
    list_flags()                   -> list[dict]
    evaluate(key, user_id, attributes) -> dict

Storage is in memory. Do not modify server.py.

See README.md for the full flag schema, the evaluation algorithm, and the pinned
deterministic bucketing formula.
"""

import threading
from typing import Any, Dict, List, Optional

# The allowed condition operators and the flag-key format. These are part of the
# contract described in README.md.
ALLOWED_OPS = {"eq", "neq", "in", "not_in", "gt", "lt", "contains"}
KEY_PATTERN = r"^[A-Za-z0-9_-]{1,64}$"

# Bucketing contract: a user maps to an integer in [0, BUCKET_SPACE). Each
# percentage point of rollout claims 100 consecutive bucket units, so rollout
# weights that sum to 100 tile [0, BUCKET_SPACE) exactly. See README.md.
BUCKET_SPACE = 10000


class FeatureFlagError(Exception):
    """Base class for all service errors."""


class ValidationError(FeatureFlagError):
    """Input is malformed or violates the flag schema (HTTP 400)."""


class NotFoundError(FeatureFlagError):
    """Referenced flag does not exist (HTTP 404)."""


class ConflictError(FeatureFlagError):
    """A flag with the same key already exists (HTTP 409)."""


class FeatureFlagService:
    """In-memory feature-flag and experiment-assignment service.

    The server calls this class concurrently, so guard shared state. You are free
    to choose the internal representation of stored flags.
    """

    def __init__(self) -> None:
        self._flags: Dict[str, dict] = {}
        self._lock = threading.RLock()

    def create_flag(self, config: dict) -> dict:
        """Validate and store a new flag.

        Raise ValidationError for an invalid config.
        Raise ConflictError if a flag with the same key already exists.
        Return the stored config.
        """
        raise NotImplementedError

    def get_flag(self, key: str) -> Optional[dict]:
        """Return the stored config for key, or None if it does not exist."""
        raise NotImplementedError

    def update_flag(self, key: str, config: dict) -> dict:
        """Replace an existing flag's config.

        Raise ValidationError for an invalid config (including a body key that
        does not match the path key).
        Raise NotFoundError if the flag does not exist.
        Return the updated config.
        """
        raise NotImplementedError

    def delete_flag(self, key: str) -> bool:
        """Delete a flag. Return True if it existed, False otherwise."""
        raise NotImplementedError

    def list_flags(self) -> List[dict]:
        """Return the stored configs for all flags."""
        raise NotImplementedError

    def evaluate(self, key: str, user_id: str, attributes: Optional[dict] = None) -> dict:
        """Evaluate a flag for a user and return the served variant.

        Raise ValidationError if user_id is not a non-empty string, or attributes
        is provided but is not an object.
        Raise NotFoundError if the flag does not exist.

        Return a dict shaped like:
            {"value": <variant>, "reason": "DISABLED"}
            {"value": <variant>, "reason": "RULE_MATCH", "rule_index": <int>}
            {"value": <variant>, "reason": "FALLTHROUGH"}
        """
        raise NotImplementedError
