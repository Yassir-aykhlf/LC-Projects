import re
from models import ServiceError
from service import WatchlistService

def dispatch(service,method,path,user,body=None,query=None,key=None):
    if not isinstance(user,str) or not user.strip():return 401,{'error':'unauthorized'}
    match=re.fullmatch(r'/watchlists(?:/([1-9][0-9]*)(?:/movies(?:/([1-9][0-9]*))?)?)?',path)
    if not match:return 404,{'error':'not_found'}
    list_id,movie_id=match.groups()
    # Bound decimal strings before conversion, including Python's digit limit.
    if list_id and (len(list_id)>19 or (len(list_id)==19 and list_id>'9223372036854775807')):
        return 404,{'error':'not_found'}
    list_id=int(list_id) if list_id else None
    try:
        if method=='POST' and path=='/watchlists':
            if not isinstance(body,dict) or set(body)!={'name'}:return 400,{'error':'invalid_input'}
            return service.create(user,body['name'])
        if list_id and '/movies' not in path:
            if method=='GET':return 200,service.get(user,list_id)
            if method=='DELETE':return service.delete(user,list_id)
            if method=='PATCH':
                if not isinstance(body,dict) or set(body)!={'name'}:return 400,{'error':'invalid_input'}
                return service.rename(user,list_id,body['name'])
        if method=='POST' and path.endswith('/movies'):
            if not isinstance(body,dict) or set(body)!={'movie_id'}:return 400,{'error':'invalid_input'}
            return service.add_movie(user,list_id,body['movie_id'])
        if method=='DELETE' and movie_id:
            if len(movie_id)>10 or (len(movie_id)==10 and movie_id>'2147483647'):
                return 400,{'error':'invalid_movie'}
            return service.remove_movie(user,list_id,int(movie_id))
        return 405,{'error':'method_not_allowed'}
    except ServiceError as error:return error.status,{'error':error.code}

def demo_service():return WatchlistService('watchlists.db')
