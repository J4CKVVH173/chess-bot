import os
from sqlite3 import OperationalError

from db_settings.connect import connect_to_db
from chess_bot.settings import BASE_DIR

conn = connect_to_db()
cursor = conn.cursor()

f = open(os.path.join(BASE_DIR, 'db_settings', 'sql', 'tables.sql'), 'r')
# из sql файла достаются все создаваемые таблицы
sqlFile = f.read()
f.close()

# строка команд разбивается на массив команд
sqlCommands = sqlFile.split(';')

# каждая команда обрабатывается отдельно
for command in sqlCommands:
    try:
        cursor.execute(command)
    except OperationalError as msg:
        print(f"Таблица пропущена: {msg}")

cursor.close()
conn.close()
