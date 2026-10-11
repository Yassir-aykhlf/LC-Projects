import os
import unittest
from unittest.mock import patch

from database import db
from test_support import BaseCase


class Cases(BaseCase):
    def test_default_configuration(self):
        """A missing configuration variable uses the documented default URL."""
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(self.service().auth_service_url, "http://internal.auth.local")

    def test_success_persists_password(self):
        """A valid code saves the new password through the database boundary."""
        service = self.service()
        code = self.invoke(service.request_reset, "user_123")
        self.assertTrue(self.invoke(service.verify_and_reset, "user_123", code, "new_pass"))
        self.assertEqual(db.get_user("user_123")["password_hash"], "hashed_new_pass")

    def test_expired_code(self):
        """A code older than the validity window cannot change a password."""
        service = self.service()
        code = self.invoke(service.request_reset, "user_123")
        self.clock.advance(31)
        self.assertFalse(self.invoke(service.verify_and_reset, "user_123", code, "new_pass"))
        self.assertEqual(db.get_user("user_123")["password_hash"], "old_hash")

    def test_replacement(self):
        """A second request replaces the earlier code with a different value."""
        service = self.service()
        first = self.invoke(service.request_reset, "user_123")
        second = self.invoke(service.request_reset, "user_123")
        self.assertNotEqual(first, second)
        self.assertFalse(self.invoke(service.verify_and_reset, "user_123", first, "new_pass"))
        self.assertEqual(db.get_reset_code("user_123")["code"], second)


if __name__ == "__main__":
    unittest.main()
