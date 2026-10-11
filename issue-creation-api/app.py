import re
from models import ServiceError
from service import IssueService

def dispatch(service,method,path,user,body=None,query=None,key=None):
    query=query or {}
    match=re.fullmatch(r'/projects/([^/]+)/issues(?:/([1-9][0-9]*))?',path)
    if not match:return 404,{'error':'not_found'}
    project,issue_id=match.groups()
    try:
        if issue_id is None and method=='POST':return service.create(user,project,body,key)
        if issue_id is None and method=='GET':
            return 200,service.list(user,project,query.get('status'),int(query.get('after_id','0')),int(query.get('limit','20')))
        if issue_id and method=='GET':return 200,service.get(user,project,int(issue_id))
        if issue_id and method=='PATCH':
            if not isinstance(body,dict) or set(body)!={'status','version'}:return 400,{'error':'invalid_input'}
            return 200,service.transition(user,project,int(issue_id),body['status'],body['version'])
        return 405,{'error':'method_not_allowed'}
    except ServiceError as error:return error.status,{'error':error.code}
    except ValueError:return 400,{'error':'invalid_input'}

def demo_service():return IssueService({'demo':['alice','bob']})
