import unittest
from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory
from pathlib import Path
from service import WatchlistService
from models import ServiceError

class Cases(unittest.TestCase):
    """Visible behavior checks for movie-watchlists."""
    def error(self,expected_status,code,fn,*args,**kwargs):
        with self.assertRaises(ServiceError) as ctx:
            fn(*args,**kwargs)
        self.assertEqual((ctx.exception.status,ctx.exception.code),(expected_status,code))

    def test_lifecycle(self):
        """Creates a watchlist and adds a movie to it."""
        with TemporaryDirectory() as tmp:
            s=WatchlistService(str(Path(tmp)/'db'))
            try:
                status,row=s.create('alice','Weekend');self.assertEqual(status,201)
                self.assertEqual(s.add_movie('alice',row['id'],10)[1]['movies'],[10])
            finally:s.close()

    def test_missing(self):
        """Reports a nonexistent watchlist as missing."""
        s=WatchlistService(':memory:')
        try:self.error(404,'list_not_found',s.get,'alice',99)
        finally:s.close()

    def test_duplicate(self):
        """Returns the duplicate-add status when a movie is already in the list."""
        s=WatchlistService(':memory:')
        try:
            _,row=s.create('alice','Films');s.add_movie('alice',row['id'],10)
            self.assertEqual(s.add_movie('alice',row['id'],10)[0],200)
        finally:s.close()

if __name__ == '__main__':
    unittest.main()
