from models import ServiceError

class BlocklistService:
    def __init__(self, keywords=(), blocked_users=()):
        # Constructor must eventually apply the same validation as replacements.
        self.keywords = list(keywords)
        self.blocked_users = list(blocked_users)

    def replace_keywords(self, keywords):
        raise NotImplementedError('Implement atomic keyword replacement')

    def replace_blocked_users(self, users):
        raise NotImplementedError('Implement manual blocklist replacement')

    def state(self, user):
        raise NotImplementedError('Return isolated moderation state')

    def check(self, user, content):
        raise NotImplementedError('Implement admission and violation tracking')
