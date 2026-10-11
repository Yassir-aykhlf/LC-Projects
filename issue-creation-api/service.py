from models import ServiceError

class IssueService:
    def __init__(self, members):
        self.members = {project:set(users) for project,users in members.items()}

    def create(self, user, project, payload, key=None):
        raise NotImplementedError('Implement authorized, retry-safe creation')

    def get(self, user, project, issue_id):
        raise NotImplementedError('Implement issue lookup')

    def transition(self, user, project, issue_id, status, version):
        raise NotImplementedError('Implement versioned lifecycle transitions')

    def list(self, user, project, status=None, after_id=0, limit=20):
        raise NotImplementedError('Implement filtered cursor pagination')
