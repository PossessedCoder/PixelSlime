import os
import sqlite3
from functools import cache, wraps

import pygame

from constants import MEDIA_URL, DB_URL


@cache  # if there are memory issues, use functools.lru_cache(maxsize={max_memory_usage_integer})
def load_image(image_name):
    return pygame.image.load(os.path.join(MEDIA_URL, image_name)).convert_alpha()


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

    def __init__(self):
        with sqlite3.connect(DB_URL) as connection:
            self._cursor = connection.cursor()

    def _commit(self):
        self._cursor.connection.commit()
