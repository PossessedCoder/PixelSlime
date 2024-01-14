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
    SET_CWW = pygame.USEREVENT + 0  # attrs: window
    CLOSE_CWW = pygame.USEREVENT + 1  # attrs: window
    FREEZE_CWW = pygame.USEREVENT + 2  # attrs: freezer
    UNFREEZE_CWW = pygame.USEREVENT + 3  # attrs: freezer
    START_SESSION = pygame.USEREVENT + 4  # attrs: uid


class Images:
    # buttons
    RUN = 'run.png'
    FORWARD = 'forward.png'
    BACK = 'back.png'
    TRASH_BIN = 'trash_bin.png'
    CLOSE_WINDOW = 'close_window.png'
    EYE = 'eye.png'
    LEVELS_PREVIEW = 'levels_preview.png'
    WRENCH = 'wrench.png'

    # tiles (and their dependencies)
    HERO = 'hero.png'
    ARROW_VECTOR = 'arrow_vector.png'
