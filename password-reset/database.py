from datetime import datetime


class MockDatabase:
    def __init__(self):
        self._users = {"user_123": {"password_hash": "old_hash_abc", "email": "user@example.com"}}
        self._reset_codes = {}

    def get_user(self, user_id: str):
        user = self._users.get(user_id)
        return user.copy() if user else None

    def update_password(self, user_id: str, new_password_hash: str):
        if user_id in self._users:
            self._users[user_id]["password_hash"] = new_password_hash

    def save_reset_code(self, user_id: str, code: str, timestamp: datetime):
        self._reset_codes[user_id] = {"code": code, "created_at": timestamp}

    def get_reset_code(self, user_id: str):
        return self._reset_codes.get(user_id)

    def clear_reset_code(self, user_id: str):
        if user_id in self._reset_codes:
            del self._reset_codes[user_id]


db = MockDatabase()
