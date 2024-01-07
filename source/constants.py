import os
from pathlib import Path

import pygame

BASE_DIR = Path(__file__).parent.parent
MEDIA_URL = os.path.join(BASE_DIR, 'media')
DB_URL = os.path.join(BASE_DIR, 'db.sqlite3')

FPS = 60
# 1920x1080 recommended
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = (pygame.display.Info().current_w, pygame.display.Info().current_h)


class UserEvents:
    # opening of a new window, must have attr "window"
    SET_CWW = pygame.USEREVENT + 1
    # closing of a current working window (remove value from windows stack)
    CLOSE_CWW = pygame.USEREVENT + 2
    # tile placed on tiles panel of the editor has been captured by user
    TILE_CAPTURED = pygame.USEREVENT + 3


class Images:
    # buttons
    FORWARD = 'forward.png'
    BACK = 'back.png'
    CLOSE_WINDOW = 'close_window.png'

    # tiles (and their dependencies)
    HERO = 'test_tile.png'
    ARROW_VECTOR = 'arrow_vector.png'
