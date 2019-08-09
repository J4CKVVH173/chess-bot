import time
import os

from telegram import Update

from chess_bot.settings import BASE_DIR


def db_has(db_object) -> bool:
    """
    Функция проверяет есть ли данные в бд
    :param db_object: результат запроса данных из бд
    :return: булевское значение, true - данные есть, false - данных нет
    """
    # ToDo переписать с учетом того что не нужно преобразовывать в список. Исправить зависимости
    return bool(list(db_object))


def parsing_user_info(update: Update) -> dict:
    """
    Функция достает основную  информацию о пользователе.
    :param update: update пришедший от телеграм содержащий основную информацию
    :return: dict
    """
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    first_name = update.message.from_user.first_name
    language_code = update.message.from_user.language_code
    chat_id = update.message.chat_id
    return dict(user_id=user_id, username=username, first_name=first_name, language_code=language_code,
                chat_id=chat_id)


def save_new_user(connect, user_info) -> None:
    """
    Метод добавляет нового пользователя в бд и фиксирует время добавления.
    :param connect: коннект к бд
    :param user_info: информация об юзере ввиде объекта
    :return: None
    """
    enter_time = time.time()
    value = (user_info['username'], user_info['first_name'], enter_time, user_info['user_id'],
             user_info['language_code'], user_info['chat_id'])
    with connect as cursor, open(os.path.join(BASE_DIR, 'db_settings', 'sql', 'add_user.sql'), 'r') as f:
        # достаем код для записи данных
        sql_to_write = f.read()
        # записываем данные
        cursor.execute(sql_to_write, value)
