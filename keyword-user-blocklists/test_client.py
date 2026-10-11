import unittest
from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory
from pathlib import Path
from service import BlocklistService
from models import ServiceError

class Cases(unittest.TestCase):
    """Visible behavior checks for keyword-user-blocklists."""
    def error(self,expected_status,code,fn,*args,**kwargs):
        with self.assertRaises(ServiceError) as ctx:
            fn(*args,**kwargs)
        self.assertEqual((ctx.exception.status,ctx.exception.code),(expected_status,code))

    def test_keyword(self):
        """Rejects a case-insensitive keyword match and adds one strike."""
        s=BlocklistService(['spam']);self.assertEqual(s.check('alice','SPAM offer'),dict(allowed=False,reason='keyword',matches=['spam'],strikes=1))

    def test_manual_block(self):
        """Rejects clean content from a manually blocked user."""
        self.assertEqual(BlocklistService([],['alice']).check('alice','hello')['reason'],'user_blocked')

    def test_clean_content(self):
        """Allows content that contains no configured keyword."""
        self.assertTrue(BlocklistService(['spam']).check('alice','hello')['allowed'])

if __name__ == '__main__':
    unittest.main()
