import os
import time
import chess
import chess.svg
import cairosvg
import io
import sqlite3

from telegram import Update, Bot

from chess_bot.extra_func import db_has, parsing_user_info, save_new_user
from chess_bot.settings import BASE_DIR, HAVE_NOT_BOARD, HAVE_GAME, BOARD_DELETE

from db_settings.connect import connect_to_db


def command_start(bot: Bot, update: Update) -> None:
    """
    Функция вызываемая на команду /start
    :param bot: объект класса Bot, управляет ботом
    :param update: объекта класса Update, содержит информацию об обновлении
    :return: None
    """
    # создаем соединение с бд
    conn = connect_to_db()

    # парсим всю необходимую информацию из updater
    user_info = parsing_user_info(update)

    # достаем sql для поиска пользователя по id
    with open(os.path.join(BASE_DIR, 'db_settings', 'sql', 'get_user_by_user_id.sql'), 'r') as f, conn as cursor:
        sql_get_usr_by_id = f.read()
        user = cursor.execute(sql_get_usr_by_id, (user_info['user_id'],))

    # если в бд еще нет такого пользователя, то записываем его
    if not db_has(user):
        save_new_user(conn, user_info)

    # ToDO Вынести текстовку в сетинги.
    bot.send_message(chat_id=update.message.chat_id, text=f'Welcome, {user_info["username"]}. Bot still in development')


def command_play(bot: Bot, update: Update) -> None:
    """
    КОлбэк для команды play. Создает доску и подготоваливает все для начала игры.
    :param bot: объект класса Bot, управляет ботом
    :param update: объекта класса Update, содержит информацию об обновлении
    :return: None
    """
    # создаем соединение с бд
    conn = connect_to_db()
    user_id = update.message.from_user.id
    board = chess.Board()
    notation_fe = board.fen()
    output_png = cairosvg.svg2png(bytestring=chess.svg.board(board=board))
    with conn as cursor, open(os.path.join(BASE_DIR, 'db_settings', 'sql', 'create_board.sql'), 'r') as f:
        sql_create_board = f.read()
        try:
            cursor.execute(sql_create_board, (notation_fe, user_id))
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY" in str(e):
                # если ошибка ключа, значит юзера еще нет, по этому создаем юзера и привязываем к нему
                # доску
                user_info = parsing_user_info(update)
                save_new_user(conn, user_info)
                cursor.execute(sql_create_board, (notation_fe, user_id))
            if "UNIQUE" in str(e):
                bot.send_message(chat_id=update.message.chat_id, text=HAVE_GAME)
                return

    # байтовую строку конвертим в io чтобы можно было скормить его send_photo
    with io.BytesIO(output_png) as image:
        bot.send_photo(chat_id=update.message.chat_id, photo=image)


def command_help(bot: Bot, update: Update) -> None:
    """
    Команда возвращает список всех команд и описание их использования.
    :param bot: объект класса Bot, управляет ботом
    :param update: объекта класса Update, содержит информацию об обновлении
    :return: None
    """
    text = """
    Bot in active development. It will be work soon.
/start - initializes the base parameters
        
/play - creates a clear board for a new game. If the game is already exist does not create a new one
        
/board - returns a board of current game. If no games then returns nothing.

After run the game, you can move just typing commands to the chat. Example - e2e4 will move pawn from 
e2 to e4.
    """
    bot.send_message(chat_id=update.message.chat_id, text=text)


def command_board(bot: Bot, update: Update) -> None:
    """
    Метод возвращает текущее изображение игровой доски или сообщение что она отсутсвует.
    :param bot: объект класса Bot, управляет ботом
    :param update: объекта класса Update, содержит информацию об обновлении
    :return: None
    """
    # создаем соединение с бд
    conn = connect_to_db()
    user_id = update.message.from_user.id

    with open(os.path.join(BASE_DIR, 'db_settings', 'sql', 'get_board.sql'), 'r') as f, conn as cursor:
        sql_get_board = f.read()
        board = cursor.execute(sql_get_board, (user_id,))

    # записываем объект курсора в виде массива в переменную. это массив картежей
    board_list = list(board)
    if db_has(board_list):
        # достаем доску, на одного игрока, одна доска [(feh,)]
        board = chess.Board(board_list[0][0])
        # получаем изображение доски преобразованное из svg в png
        output_png = cairosvg.svg2png(bytestring=chess.svg.board(board=board))
        with io.BytesIO(output_png) as image:
            bot.send_photo(chat_id=update.message.chat_id, photo=image)
    else:
        bot.send_message(chat_id=update.message.chat_id, text=HAVE_NOT_BOARD)


def command_move(bot: Bot, update: Update) -> None:
    """
    Метод отвечает за движение.
    :param bot: объект класса Bot, управляет ботом
    :param update: объекта класса Update, содержит информацию об обновлении
    :return: None
    """
    # создаем соединение с бд
    conn = connect_to_db()
    user_id = update.message.from_user.id
    text = update.message.text
    chat_id = update.message.chat_id

    with open(os.path.join(BASE_DIR, 'db_settings', 'sql', 'get_board.sql'), 'r') as f, conn as cursor:
        sql_get_board = f.read()
        board = cursor.execute(sql_get_board, (user_id,))

        # записываем объект курсора в виде массива в переменную. это массив картежей
        board_list = list(board)
        if db_has(board_list):
            # достаем доску, на одного игрока, одна доска [(feh,)]
            board = chess.Board(board_list[0][0])
            board.push_uci(text)
            # получаем изображение доски преобразованное из svg в png
            output_png = cairosvg.svg2png(bytestring=chess.svg.board(board=board))
            with io.BytesIO(output_png) as image, \
                    open(os.path.join(BASE_DIR, 'db_settings', 'sql', 'update_board.sql'), 'r') as file, conn as curs:
                sql_update_board = file.read()
                curs.execute(sql_update_board, (board.fen(), user_id))
                bot.send_photo(chat_id=chat_id, photo=image)
        else:
            bot.send_message(chat_id=chat_id, text=HAVE_NOT_BOARD)


def command_turn(bot: Bot, update: Update):
    """
    Метод определяет чей сейчас ход.
    :param bot: объект класса Bot, управляет ботом
    :param update: объекта класса Update, содержит информацию об обновлении
    :return: None
    """
    # создаем соединение с бд
    conn = connect_to_db()
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    with open(os.path.join(BASE_DIR, 'db_settings', 'sql', 'get_board.sql'), 'r') as f, conn as cursor:
        sql_get_board = f.read()
        board = cursor.execute(sql_get_board, (user_id,))
        # записываем объект курсора в виде массива в переменную. это массив картежей
        board_list = list(board)
        if db_has(board_list):
            # достаем доску, на одного игрока, одна доска [(feh,)]
            board = chess.Board(board_list[0][0])
            # определение стороны хода
            turn = 'White' if board.turn else 'Black'
            bot.send_message(chat_id=chat_id, text=turn)
        else:
            bot.send_message(chat_id=chat_id, text=HAVE_NOT_BOARD)


def command_end_game(bot: Bot, update: Update):
    """
    Метод определяет чей сейчас ход.
    :param bot: объект класса Bot, управляет ботом
    :param update: объекта класса Update, содержит информацию об обновлении
    :return: None
    """
    # создаем соединение с бд
    conn = connect_to_db()
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    with open(os.path.join(BASE_DIR, 'db_settings', 'sql', 'delete_board.sql'), 'r') as f, conn as cursor:
        sql_delete_board = f.read()
        cursor.execute(sql_delete_board, (user_id,))
        # записываем объект курсора в виде массива в переменную. это массив картежей
        bot.send_message(chat_id=chat_id, text=BOARD_DELETE)


def command_is_check(bot: Bot, update: Update):
    """
    Метод проверяет, есть ли шах у текущей стороны.
    :param bot: объект класса Bot, управляет ботом
    :param update: объекта класса Update, содержит информацию об обновлении
    :return: None
    """
    # создаем соединение с бд
    conn = connect_to_db()
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    with open(os.path.join(BASE_DIR, 'db_settings', 'sql', 'get_board.sql'), 'r') as f, conn as cursor:
        sql_get_board = f.read()
        board = cursor.execute(sql_get_board, (user_id,))
        # записываем объект курсора в виде массива в переменную. это массив картежей
        board_list = list(board)
        if db_has(board_list):
            # достаем доску, на одного игрока, одна доска [(feh,)]
            board = chess.Board(board_list[0][0])
            # определение стороны хода
            check = 'Yes' if board.is_check() else 'No'
            bot.send_message(chat_id=chat_id, text=check)
        else:
            bot.send_message(chat_id=chat_id, text=HAVE_NOT_BOARD)
