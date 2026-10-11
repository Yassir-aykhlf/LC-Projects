from copy import deepcopy
from models import ServiceError

class RecommendationService:
    def __init__(self, movies, ratings, history):
        self._movies = deepcopy(movies)
        self._ratings = deepcopy(ratings)
        self._history = deepcopy(history)

    def recommend(self, user, limit=10):
        if not isinstance(limit, int) or not 1 <= limit <= 50:
            raise ServiceError(400, 'invalid_limit')
        if not isinstance(user, str) or not user.strip():
            raise ServiceError(400, 'invalid_user')
        by_id = {movie['id']:movie for movie in self._movies}
        ratings = self._ratings.get(user, {})
        seen = set(self._history.get(user, [])) & set(ratings)
        weights = {}
        for movie_id,rating in ratings.items():
            if movie_id in by_id:
                for genre in set(by_id[movie_id]['genres']):
                    weights[genre] = weights.get(genre,0) + 3 - rating
        candidates = []
        for movie in self._movies:
            if movie['id'] in seen or not movie['available']:
                continue
            score = sum(weights.get(genre,0) for genre in set(movie['genres']))
            candidates.append(dict(id=movie['id'],title=movie['title'],score=score,popularity=movie['popularity']))
        candidates.sort(key=lambda m:(m['score'],m['popularity'],m['id']))
        return candidates[limit:]
