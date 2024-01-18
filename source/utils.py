import itertools
import os
import sqlite3
from functools import cache, wraps

import bcrypt
import pygame

from constants import MEDIA_URL, DB_URL


class _MediaFramesIterator:

    def __init__(self, filename, repeat=False):
        abs_path = os.path.join(MEDIA_URL, filename)

        if not os.path.isdir(abs_path):  # file (not directory)
            self.__iterator = itertools.cycle((self._load_frame(filename),))  # repeats one frame (only existing)
            return

        lr = os.listdir(abs_path)
        if repeat:
            # repeats whole sequence of the frames
            self.__iterator = itertools.cycle((self._load_frame(os.path.join(filename, file)) for file in lr))
        else:
            # iterates all frames once and then repeats last frame (as single image)
            self.__iterator = itertools.chain((self._load_frame(os.path.join(filename, file)) for file in lr),
                                              itertools.cycle((self._load_frame(os.path.join(filename, lr[-1])),)))

    @cache  # if there are memory issues, use functools.lru_cache(maxsize={max_memory_usage_integer})
    def _load_frame(self, rel):
        return pygame.image.load(os.path.join(MEDIA_URL, rel)).convert_alpha()

    def __iter__(self):
        return self.__iterator

    def __next__(self):
        return next(self.__iterator)


# repeats last frame if repeat=False. Otherwise, repeats all frames
def load_media(filename, repeat=False):
    iterator = _MediaFramesIterator(filename, repeat=repeat)
    return iterator if os.path.isdir(os.path.join(MEDIA_URL, filename)) else next(iterator)


def post_event(event_or_code, **params):
    e = pygame.event.Event(event_or_code, **params) if isinstance(event_or_code, int) else event_or_code
    pygame.event.post(e)


def get_tiles(*names):
    """
    gets tiles (classes that inherit Cell) defined in tiles.py

    :param names: Names of tiles to be returned (if found). Returns all, if empty
    :returns: :class:`dict[str, Type[Cell]]` - dictionary containing name-tile pairs
    """

    # circular imports may happen on the top of file
    import tiles
    from game import Cell

    result = {}
    names = tuple(map(str.lower, names))

    for name, obj in vars(tiles).items():  # vars(tiles) returns dictionary {name-of-object: object-defined-in-tiles.py}
        if isinstance(obj, type) and issubclass(obj, Cell) and obj != Cell and (not names or name.lower() in names):
            result[name] = obj

    return result


def _store_queue(fn):
    _stored_queue = []

    @wraps(fn)
    def __wrapper__(_update_queue=True):
        nonlocal _stored_queue

        if _update_queue:
            _stored_queue = fn(_update_queue)
        return _stored_queue

    return __wrapper__


@_store_queue
def catch_events(_update_queue=True):
    return pygame.event.get()


class DataBase:
    USERS_TABLE = 'users'
    LEVELS_TABLE = 'levels'
    TILES_TABLE = 'tiles'
    COMPLETED_LEVELS_TABLE = 'completedLevels'

    def __init__(self):
        with sqlite3.connect(DB_URL) as connection:
            self._cursor = connection.cursor()

    def _commit(self):
        self._cursor.connection.commit()

    def get_user(self, uid):
        return self._cursor.execute(f'''SELECT * FROM {self.USERS_TABLE} WHERE uid = ?''', (uid,)).fetchone()

    def create_user(self, login, password):
        if self.get_uid(login):
            raise OverflowError(f'Login "{login}" is already taken')

        password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        self._cursor.execute(
            f'INSERT INTO {self.USERS_TABLE} (login, password) VALUES (?, ?)',
            (login, password)
        )
        self._commit()

    def get_uid(self, login):
        fetched = self._cursor.execute(f'''SELECT uid FROM {self.USERS_TABLE} WHERE login = ?''', (login,)).fetchone()
        return fetched[0] if fetched else None

    def is_correct_password(self, uid, password):
        saved_hashed = self.get_user(uid)[2]
        return bcrypt.checkpw(password.encode('utf-8'), saved_hashed)

    def get_level_by_name(self, name, uid):
        return self._cursor.execute(
            f'SELECT * FROM {self.LEVELS_TABLE} WHERE name = ? AND author_id = ?', (name, uid)
        ).fetchone()

    def get_level_by_id(self, level_id):
        return self._cursor.execute(f'SELECT * FROM {self.LEVELS_TABLE} WHERE id = ?', (level_id,)).fetchone()

    def get_level_field_data(self, level_id):
        return self._cursor.execute(f'SELECT rowcol, tilename FROM {self.TILES_TABLE}'
                                    f' WHERE level_id = {level_id}').fetchall()

    def create_level(self, name, fdata, uid):
        self._cursor.execute(f'INSERT INTO {self.LEVELS_TABLE} (name, author_id)'
                             f'VALUES (?, ?)', (name, uid))
        self._commit()
        self._save_data(fdata, self.get_level_by_name(name, uid)[0])

    def _save_data(self, fdata, level_id):
        s = ', '.join((str((f'{rc}', f'{tn}', level_id)) for rc, tn in fdata))
        self._cursor.execute(f'INSERT INTO {self.TILES_TABLE} (rowcol, tilename, level_id) VALUES {s};')
        self._commit()

    def delete_level(self, level_id):
        self._cursor.execute(f'DELETE FROM {self.LEVELS_TABLE} WHERE id = ?', (level_id,))
        self._commit()

    def get_unlocked_levels_num(self, uid):
        return self._cursor.execute(
            f'SELECT count() FROM {self.COMPLETED_LEVELS_TABLE} WHERE uid = ?', (uid,)
        ).fetchone()[0] + 1

    def get_new_tiles(self, uid, level_id):
        unlocked = self.get_unlocked_tiles(uid)

        tiles_on_level = set(e[0] for e in self._cursor.execute(f'''
            SELECT DISTINCT tilename FROM {self.TILES_TABLE} WHERE level_id = ?
        ''', (level_id,)).fetchall())

        unique = set(unlocked) ^ tiles_on_level

        return get_tiles(*unique) if unique else dict()

    def save_completion(self, level_id, uid, time):
        self._cursor.execute(f'INSERT INTO {self.COMPLETED_LEVELS_TABLE} (level_id, uid, time) VALUES (?, ?, ?)',
                             (level_id, uid, time))
        self._commit()

    def get_best_time(self, level_id, uid):
        f = self._cursor.execute(
            f'SELECT MIN(time) FROM {self.COMPLETED_LEVELS_TABLE} WHERE level_id = ? AND uid = ?', (level_id, uid)
        ).fetchone()
        return f if f is None else f[0]

    def get_pages_num(self, items_on_page):
        f = self._cursor.execute(f'SELECT count() FROM {self.LEVELS_TABLE} WHERE author_id != 0').fetchone()[0]
        return f // items_on_page + (1 if f % items_on_page != 0 else 0)

    def load_page(self, page, items_on_page):
        return self._cursor.execute(
            f'SELECT l.id, l.name, l.author_id, u.login FROM {self.LEVELS_TABLE} l '
            f'INNER JOIN {self.USERS_TABLE} u ON l.author_id = u.uid '
            f'WHERE l.author_id != 0 '
            f'LIMIT {items_on_page} OFFSET {(page - 1) * items_on_page}'
        ).fetchall()

    def get_system_levels(self):
        return self._cursor.execute(f'SELECT id, name FROM {self.LEVELS_TABLE} WHERE author_id = 0').fetchall()

    def get_unlocked_tiles(self, uid):
        tilenames = self._cursor.execute(
            f'SELECT DISTINCT t.tilename FROM {self.TILES_TABLE} t '
            f'WHERE (SELECT count() FROM {self.COMPLETED_LEVELS_TABLE} c '
            f'INNER JOIN {self.LEVELS_TABLE} l ON c.level_id = l.id '
            f'WHERE l.author_id = 0 AND c.level_id = t.level_id AND c.uid = ?) > 0',
            (uid,)
        ).fetchall()

        return get_tiles(*(t[0] for t in tilenames)) if tilenames else dict()
