import unittest
from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory
from pathlib import Path
from service import IssueService
from models import ServiceError

class Cases(unittest.TestCase):
    """Visible behavior checks for issue-creation-api."""
    def error(self,expected_status,code,fn,*args,**kwargs):
        with self.assertRaises(ServiceError) as ctx:
            fn(*args,**kwargs)
        self.assertEqual((ctx.exception.status,ctx.exception.code),(expected_status,code))

    def test_create(self):
        """Saves a new open issue with a trimmed title and returns it on lookup."""
        s=IssueService({'demo':['alice']});status,row=s.create('alice','demo',{'title':' Fix login '})
        self.assertEqual((status,row['title'],row['status']),(201,'Fix login','open'))
        self.assertEqual(s.get('alice','demo',row['id']),row)

    def test_retry(self):
        """Returns the existing issue when a creation request repeats its idempotency key."""
        s=IssueService({'demo':['alice']});_,row=s.create('alice','demo',{'title':'Bug'},'retry-1')
        self.assertEqual(s.create('alice','demo',{'title':'Bug'},'retry-1'),(200,row))

    def test_unauthorized(self):
        """Rejects issue creation without a user identity."""
        self.error(401,'unauthorized',IssueService({'demo':['alice']}).create,'','demo',{'title':'Bug'})

if __name__ == '__main__':
    unittest.main()
