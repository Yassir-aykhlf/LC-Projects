from models import ServiceError

class RiskEngine:
    def evaluate(self, rating, value_cents, account_age_days):
        if (not isinstance(rating, int) or not 1 <= rating <= 5 or
            type(value_cents) is not int or value_cents < 0 or
            type(account_age_days) is not int or account_age_days < 0):
            raise ServiceError(400, 'invalid_input')
        rating_points = {1: 0, 2: 10, 3: 20, 4: 30, 5: 40}[rating]
        value_points = 30 if value_cents > 50000 else 15 if value_cents >= 10000 else 0
        age_points = 25 if account_age_days < 30 else 10 if account_age_days < 180 else 0
        score = rating_points + value_points + age_points
        decision = 'reject' if score > 60 else 'manual_review' if score >= 30 else 'approve'
        return {'score': score, 'decision': decision,
                'components': {'rating': rating_points, 'value': value_points, 'age': age_points}}

    def evaluate_many(self, records):
        results = []
        for record in records:
            try:
                if not isinstance(record, dict) or set(record) != {'rating', 'value_cents', 'account_age_days'}:
                    raise ServiceError(400, 'invalid_input')
                results.append({'result': self.evaluate(**record), 'error': None})
            except ServiceError as error:
                results.append({'result': None, 'error': None})
        return results
