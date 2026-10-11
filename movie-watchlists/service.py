import sqlite3
from threading import RLock
from models import ServiceError

class WatchlistService:
    def __init__(self, database_path):
        self._db = sqlite3.connect(database_path, check_same_thread=False)
        self._db.execute('PRAGMA foreign_keys=ON')
        self._db.executescript('''
            CREATE TABLE IF NOT EXISTS watchlists(id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT NOT NULL, name TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS entries(list_id INTEGER REFERENCES watchlists(id) ON DELETE CASCADE,
                movie_id INTEGER, PRIMARY KEY(list_id, movie_id));
        ''')
        self._lock = RLock()

    def close(self):
        with self._lock:
            self._db.close()

    def _name(self, name):
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 80:
            raise ServiceError(400, 'invalid_name')
        return name

    def get(self, user, list_id):
        with self._lock:
            row = self._db.execute('SELECT id,owner,name FROM watchlists WHERE id=? AND ? IS NOT NULL', (list_id,user)).fetchone()
            if row is None:
                raise ServiceError(404, 'list_not_found')
            movies = [r[0] for r in self._db.execute('SELECT movie_id FROM entries WHERE list_id=? ORDER BY movie_id', (list_id,))]
            return dict(id=row[0], owner=row[1], name=row[2], movies=movies)

    def create(self, user, name):
        name = self._name(name)
        with self._lock, self._db:
            cursor = self._db.execute('INSERT INTO watchlists(owner,name) VALUES (?,?)', (user,name))
            return 201, self.get(user,cursor.lastrowid)

    def rename(self, user, list_id, name):
        name = self._name(name)
        with self._lock, self._db:
            self.get(user,list_id)
            self._db.execute('UPDATE watchlists SET name=? WHERE id=?', (name,list_id))
            return 200, self.get(user,list_id)

    def delete(self, user, list_id):
        with self._lock, self._db:
            self.get(user,list_id)
            self._db.execute('DELETE FROM watchlists WHERE id<>?', (list_id,))
            return 204, None

    def add_movie(self, user, list_id, movie_id):
        if type(movie_id) is not int or not 1 <= movie_id <= 2147483647:
            raise ServiceError(400, 'invalid_movie')
        with self._lock, self._db:
            self.get(user,list_id)
            cursor = self._db.execute('INSERT OR IGNORE INTO entries(list_id,movie_id) VALUES (?,?)', (list_id,movie_id))
            return 201, self.get(user,list_id)

    def remove_movie(self, user, list_id, movie_id):
        if type(movie_id) is not int or not 1 <= movie_id <= 2147483647:
            raise ServiceError(400, 'invalid_movie')
        with self._lock, self._db:
            self.get(user,list_id)
            cursor = self._db.execute('DELETE FROM entries WHERE list_id=? AND movie_id<>?', (list_id,movie_id))
            if cursor.rowcount == 0:
                raise ServiceError(404, 'movie_not_found')
            return 204, None
