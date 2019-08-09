import sqlite3

from chess_bot.settings import DB_FILE_NAME


def connect_to_db():
    """
    Метод производит подключение к базе данных
    :return: cursor, функция-курсор для работы с БД к которой было произведено подключение и conn само подключение
    """
    conn = sqlite3.connect(DB_FILE_NAME)
    conn.execute("PRAGMA foreign_keys = 1")  # подключаем использование fk

    return conn
