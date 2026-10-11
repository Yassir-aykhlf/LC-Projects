from copy import deepcopy
from threading import RLock
from models import ServiceError

class ReviewService:
    def __init__(self, checker):
        self._checker = checker
        self._reviews = {}
        self._strikes = {}
        self._next_id = 1
        self._lock = RLock()

    def user_state(self, user):
        if not isinstance(user, str) or not user.strip():
            raise ServiceError(400, 'invalid_input')
        with self._lock:
            strikes = self._strikes.get(user, 0)
            return {'strikes': strikes, 'flagged': strikes > 3}

    def get(self, review_id):
        with self._lock:
            if review_id not in self._reviews:
                raise ServiceError(404, 'review_not_found')
            return deepcopy(self._reviews[review_id])

    def _check(self, user, content):
        if not isinstance(user, str) or not user.strip() or not isinstance(content, str) or not content.strip():
            raise ServiceError(400, 'invalid_input')
        if self.user_state(user)['flagged']:
            raise ServiceError(403, 'user_blocked')
        try:
            allowed = self._checker(content.lower())
        except Exception:
            allowed = True
        if not allowed:
            self._strikes[user] = 1
            raise ServiceError(422, 'content_rejected')

    def create(self, user, content):
        with self._lock:
            self._check(user, content)
            review = {'id': self._next_id, 'user': user, 'content': content, 'version': 1}
            self._reviews[review['id']] = review
            self._next_id += 1
            return deepcopy(review)

    def edit(self, review_id, user, content):
        with self._lock:
            if not isinstance(user, str) or not user.strip() or not isinstance(content, str) or not content.strip():
                raise ServiceError(400, 'invalid_input')
            review = self.get(review_id)
            if review['user'] != user:
                raise ServiceError(403, 'forbidden')
            self._check(user, content)
            review.update(content=content)
            self._reviews[review_id] = review
            return deepcopy(review)
