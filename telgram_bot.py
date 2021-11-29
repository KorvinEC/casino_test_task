import logging
import sqlite3
import os
from db.db import init_db
from telegram import \
    KeyboardButton, \
    Update, \
    ReplyKeyboardMarkup
from telegram.ext import \
    Updater, \
    CommandHandler, \
    CallbackQueryHandler, \
    CallbackContext, \
    PicklePersistence

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = '2132310092:AAFCSnJs4n-IbRU4S_u6l0spz-hCLp3H9FA'


def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [[
        KeyboardButton(text="/get_info"),
        KeyboardButton(text="/get_key")
    ]]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    print(context.user_data)

    if not context.user_data:
        context.user_data['token'] = 10

    text = f'Hello! Your token count is {context.user_data["token"]}'

    update.message.reply_text(text, reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")


def help_command(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    text = '/get_info - show you your information and avilable tokens\n' \
           '/get_key - get xPub key'
    update.message.reply_text(text)


def get_info_command(update: Update, context: CallbackContext) -> None:
    text = f'Tokens: {context.user_data["token"]}'
    update.message.reply_text(text)


def get_key_command(update: Update, context: CallbackContext) -> None:
    text = '+ 10 tokens'
    context.user_data['token'] += 10
    update.message.reply_text(text)


def get_data_command(update: Update, context: CallbackContext) -> None:
    if context.args:
        arg = context.args[0]
        with sqlite3.connect('sqlite3.db') as con:
            cur = con.cursor()

            cur.execute(f''' 
                SELECT (name, phone_number) FROM users
                WHERE (name = "{arg}") or (phone_number = "{arg}")
            ''')
        update.message.reply_text(f'Searched: {"asdf"}\nResult:{"asdfad"}')
    else:
        update.message.reply_text('Insert search parameters')


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.

    persistence = PicklePersistence(filename='test_task_bot')
    updater = Updater(TOKEN, persistence=persistence)
    # updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))

    updater.dispatcher.add_handler(CommandHandler('get_info', get_info_command))
    updater.dispatcher.add_handler(CommandHandler('get_key', get_key_command))
    updater.dispatcher.add_handler(CommandHandler('get_data', get_data_command))

    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':

    path_to_db = os.path.join(os.getcwd(), 'sqlite3.db')
    if not os.path.exists(path_to_db):
        logger.log(msg='DB initializing', level=logging.INFO)
        init_db()
    else:
        logger.log(msg='DB exists', level=logging.INFO)

    main()