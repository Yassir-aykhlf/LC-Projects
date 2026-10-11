import unittest
from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory
from pathlib import Path
from service import ReviewService
from models import ServiceError

class Cases(unittest.TestCase):
    """Visible behavior checks for review-moderation."""
    def error(self,expected_status,code,fn,*args,**kwargs):
        with self.assertRaises(ServiceError) as ctx:
            fn(*args,**kwargs)
        self.assertEqual((ctx.exception.status,ctx.exception.code),(expected_status,code))

    def test_clean_review(self):
        """Saves an approved review and returns it on lookup."""
        s=ReviewService(lambda text:'spam' not in text)
        a=s.create('alice','Useful product');self.assertEqual(s.get(a['id']),a)

    def test_rejected_review(self):
        """Rejects disallowed content and records one strike."""
        s=ReviewService(lambda _:False);self.error(422,'content_rejected',s.create,'alice','spam')
        self.assertEqual(s.user_state('alice')['strikes'],1)

    def test_edit(self):
        """Increments the review version after a successful edit."""
        s=ReviewService(lambda _:True);a=s.create('alice','First')
        self.assertEqual(s.edit(a['id'],'alice','Updated')['version'],2)

if __name__ == '__main__':
    unittest.main()
