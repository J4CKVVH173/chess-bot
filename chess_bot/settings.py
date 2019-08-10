import os

TG_TOKEN = os.environ['TG_TOKEN_CHESS']  # токне
TG_BASE_URL = 'https://telegg.ru/orig/bot'  # урл для обхода блокировки

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # базовый урл

DB_FILE_NAME = 'db.sqlite'

HAVE_NOT_BOARD = 'You still have not a board. Run /play command.'
HAVE_GAME = 'You already have a game.'
BOARD_DELETE = 'The game is completed.'
FEEDBACK = 'Thank you for your feedback.'
