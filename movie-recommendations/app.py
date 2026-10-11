from models import ServiceError
from service import RecommendationService

def dispatch(service,method,path,user,body=None,query=None,key=None):
    if path!='/recommendations':return 404,{'error':'not_found'}
    if method!='GET':return 405,{'error':'method_not_allowed'}
    if not isinstance(user,str) or not user.strip():return 401,{'error':'unauthorized'}
    try:return 200,{'recommendations':service.recommend(user,int((query or {}).get('limit','10')))}
    except ServiceError as error:return error.status,{'error':error.code}
    except ValueError:return 400,{'error':'invalid_limit'}

def demo_service():
    movies=[dict(id=1,title='First Laugh',genres=['comedy'],popularity=20,available=True),
            dict(id=2,title='Second Laugh',genres=['comedy'],popularity=10,available=True),
            dict(id=3,title='Night Train',genres=['drama'],popularity=30,available=True)]
    return RecommendationService(movies,{'alice':{1:5}},{'alice':[1]})
