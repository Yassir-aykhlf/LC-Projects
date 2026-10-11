import unittest
from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory
from pathlib import Path
from service import RecommendationService
from models import ServiceError

class Cases(unittest.TestCase):
    """Visible behavior checks for movie-recommendations."""
    def error(self,expected_status,code,fn,*args,**kwargs):
        with self.assertRaises(ServiceError) as ctx:
            fn(*args,**kwargs)
        self.assertEqual((ctx.exception.status,ctx.exception.code),(expected_status,code))

    def test_recommend(self):
        """Scores an unseen movie from the user's rating and excludes the rated movie."""
        movies=[dict(id=1,title='A',genres=['comedy'],popularity=1,available=True),dict(id=2,title='B',genres=['comedy'],popularity=2,available=True)]
        s=RecommendationService(movies,{'u':{1:5}},{})
        self.assertEqual(s.recommend('u'),[dict(id=2,title='B',score=2,popularity=2)])

    def test_empty(self):
        """Returns no recommendations for an empty catalogue."""
        self.assertEqual(RecommendationService([],{},{}).recommend('new'),[])

    def test_limit(self):
        """Rejects a zero result limit."""
        self.error(400,'invalid_limit',RecommendationService([],{},{}).recommend,'u',0)

if __name__ == '__main__':
    unittest.main()
