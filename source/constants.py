__all__ = (
    'BASE_DIR',
    'DB_URL',
    'FPS',
    'SCREEN_SIZE',
    'SCREEN_WIDTH',
    'SCREEN_HEIGHT',
    'MEDIA_URL',
    'UserEvents',
    'Media'
)

import os
from pathlib import Path

import pygame

BASE_DIR = Path(__file__).parent.parent
MEDIA_URL = os.path.join(BASE_DIR, 'media')
DB_URL = os.path.join(BASE_DIR, 'db.sqlite3')

FPS = 60
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = (1920, 1080)


class UserEvents:
    # pygame has limitations on events num: maximum of 9 events is only available (ids from 24 to 32),
    # so this class should contain only vital attributes
    SET_CWW = pygame.USEREVENT + 0  # attrs: window
    CLOSE_CWW = pygame.USEREVENT + 1  # attrs: window
    FREEZE_CWW = pygame.USEREVENT + 2  # attrs: freezer
    UNFREEZE_CWW = pygame.USEREVENT + 3  # attrs: freezer
    START_SESSION = pygame.USEREVENT + 4  # attrs: uid
    SAVE_LEVEL = pygame.USEREVENT + 5  # attrs: level_id, fdata, pack
    DELETE_LEVEL = pygame.USEREVENT + 6  # attrs: level_id
    LEVEL_COMPLETED = pygame.USEREVENT + 7  # attrs: level_id, time
    RUN_WITH_UID = pygame.USEREVENT + 8  # attrs: runner


class Media:
    # buttons
    RUN = 'run.png'
    FORWARD = 'forward.png'
    BACK = 'back.png'
    TRASH_BIN = 'trash_bin.png'
    CLOSE_WINDOW = 'close_window.png'
    EYE = 'eye.png'
    LEVELS_PREVIEW = 'levels_preview.png'
    WRENCH = 'wrench.png'
    SAVE = 'save.png'
    CLEAR = 'clear.png'
    CROSS = 'cross.png'
    DOCUMENT = 'saved_levels.png'

    # packs
    LAVA_PACK = 'lava_pack'
    ROCK_PACK = 'rock_pack'
    SKY_PACK = 'sky_pack'
    PURPLE_PACK = 'purple_pack'

    HERO_STATIC = '{}/hero.png'
    HERO_ARROW_VECTOR = '{}/arrow_vector.png'
    BACKGROUND = '{}/background.png'
    BLOCK = '{}/block.png'
    END_LEVEL = '{}/opened_door.png'
    SPIKE = '{}/spike.png'

    # texts
    TITLE = 'title.gif'
    LABEL_EDITOR = 'label_editor.gif'
    LABEL_LEVELS = 'label_levels.gif'

    # decorations
    SUCCESS = 'successful.png'
    FAILED = 'failed.png'
    CLOCK = 'clock.png'
    LOCKED = 'locked.png'
    UNLOCKED = 'unlocked.png'
