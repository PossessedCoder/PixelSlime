import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
MEDIA_URL = os.path.join(BASE_DIR, 'media')
DB_URL = os.path.join(BASE_DIR, 'db.sqlite3')

FPS = 60
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = (1920, 1080)  # 1920x1080 px


class __ImagesMeta(type):

    def __new__(cls, *args):
        __mcl = super().__new__(cls, *args)

        for attr_name in __mcl.__dict__:
            try:
                abs_path = os.path.join(MEDIA_URL, getattr(__mcl, attr_name))
            except TypeError:
                continue
            if not os.path.isfile(abs_path):  # ignore not path-like attributes
                continue
            setattr(__mcl, attr_name, abs_path)

        return __mcl


class Images(metaclass=__ImagesMeta):
    # all the names below will be converted to absolute paths on class creation by metaclass

    HERO = 'test_tile.png'
    ARROW_VECTOR = 'arrow_vector.png'
    FORWARD = 'forward.png'
    BACK = 'back.png'
    CLOSE = 'close_window.png'
