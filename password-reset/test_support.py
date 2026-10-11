import copy
import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from auth_service import PasswordResetService
from database import db


class Clock:
    def __init__(self):
        self.current = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return self.current

    def advance(self, seconds):
        self.current += timedelta(seconds=seconds)


class BaseCase(unittest.TestCase):
    def setUp(self):
        previous_users, previous_codes = db._users, db._reset_codes
        self.addCleanup(setattr, db, "_users", previous_users)
        self.addCleanup(setattr, db, "_reset_codes", previous_codes)
        db._users = {
            "user_123": {"password_hash": "old_hash", "email": "user@example.com"},
            "user_456": {"password_hash": "other_hash", "email": "other@example.com"},
        }
        db._reset_codes = {}
        self.enterContext(patch.dict(os.environ, {"INTERNAL_AUTH_URL": "http://internal.auth.local"}))
        self.clock = Clock()

    def invoke(self, function, *args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as error:
            self.fail(f"The operation should complete without {type(error).__name__}.")

    def service(self):
        return self.invoke(PasswordResetService, clock=self.clock)

    def snapshot(self):
        return copy.deepcopy((db._users, db._reset_codes))
