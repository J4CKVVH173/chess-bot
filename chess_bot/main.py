from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


from chess_bot.commands import command_start, command_play, command_help, command_board, command_move, command_turn,\
    command_end_game, command_is_check
from chess_bot.settings import TG_TOKEN, TG_BASE_URL


def main() -> None:
    """
    Основная функция. В ней создается бот и навешиваются все хендлеры.
    :return: None
    """
    bot = Bot(token=TG_TOKEN, base_url=TG_BASE_URL)
    updater = Updater(bot=bot)

    start_handler = CommandHandler("start", command_start)
    play_handler = CommandHandler("play", command_play)
    help_handler = CommandHandler("help", command_help)
    board_handler = CommandHandler("board", command_board)
    turn_handler = CommandHandler("turn", command_turn)
    end_game_handler = CommandHandler("endGame", command_end_game)
    have_check__handler = CommandHandler("haveCheck", command_is_check)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(play_handler)
    updater.dispatcher.add_handler(help_handler)
    updater.dispatcher.add_handler(board_handler)
    updater.dispatcher.add_handler(turn_handler)
    updater.dispatcher.add_handler(end_game_handler)
    updater.dispatcher.add_handler(have_check__handler)

    move_handler = MessageHandler(Filters.text, command_move)

    updater.dispatcher.add_handler(move_handler)

    updater.start_polling()
    updater.idle()
