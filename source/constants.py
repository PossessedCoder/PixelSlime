import os
from pathlib import Path

import pygame

BASE_DIR = Path(__file__).parent.parent
MEDIA_URL = os.path.join(BASE_DIR, 'media')
DB_URL = os.path.join(BASE_DIR, 'db.sqlite3')

FPS = 60
# 1920x1080 recommended
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = (1920, 1080)


class UserEvents:
    # pygame has limitations on events num: maximum of 9 events is only available (ids from 24 to 32),
    # so this class should contain only vital attributes
    SET_CWW = pygame.USEREVENT + 0
    CLOSE_CWW = pygame.USEREVENT + 1


class Images:
    # buttons
    RUN = 'run.png'
    FORWARD = 'forward.png'
    BACK = 'back.png'
    TRASH_BIN = 'trash_bin.png'
    CLOSE_WINDOW = 'close_window.png'

    # tiles (and their dependencies)
    HERO = 'hero.png'
    ARROW_VECTOR = 'arrow_vector.png'
