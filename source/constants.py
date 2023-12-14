import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
MEDIA_URL = os.path.join(BASE_DIR, 'media')
DB_URL = os.path.join(BASE_DIR, 'db.sqlite3')

FPS = 60
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = (1920, 1080)  # 1920x1080 px
