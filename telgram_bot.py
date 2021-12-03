import logging
import sqlite3
import os
import requests
import html
import random
from dotenv import load_dotenv
from db import init_db

from telegram import \
    KeyboardButton, \
    Update, \
    ReplyKeyboardMarkup
from telegram.ext import \
    Updater, \
    CommandHandler, \
    CallbackContext, \
    PicklePersistence

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
api_key = os.getenv('API_KEY')


def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [[
        KeyboardButton(text="/get_info"),
        KeyboardButton(text="/get_key")
    ]]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    if not context.user_data:
        context.user_data['token'] = 10

    text = f'Hello! Your token count is {context.user_data["token"]}.\n' \
           f'Type /help for more info.'

    update.message.reply_text(text, reply_markup=reply_markup)


def help_command(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    text = '/get_info - show you your information and available tokens.\n' \
           '/get_key - get xPub key.\n' \
           '/get_data [key] - Search in database. On successful search you lose one token.'
    update.message.reply_text(text)


def get_info_command(update: Update, context: CallbackContext) -> None:
    ret_str = f'Tokens: {context.user_data["token"]}\n'

    res = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
    for cur in ['USD', 'GBP', 'EUR']:

        ret_str += f"{html.unescape(res.json()['bpi'][cur]['symbol'])} " \
                   f"{res.json()['bpi'][cur]['code']}: " \
                   f"{res.json()['bpi'][cur]['rate_float']}\n"

    update.message.reply_text(ret_str)


def payment_check():
    return True if random.randint(0, 1) else False


def payment_check_cycle(context: CallbackContext):
    update, user_data = context.job.context
    if user_data['timer_count'] > 0:
        logger.log(msg=f"Checking ... {user_data['timer_count']}", level=logging.INFO)
        if payment_check():
            user_data['token'] += 10
            update.message.reply_text(f'Payment successful\nTokens: {user_data["token"]}')
            logger.log(msg="Payment successful", level=logging.INFO)
            context.job.schedule_removal()
        user_data['timer_count'] -= 1
    else:
        logger.log(msg="Payment was not complete", level=logging.INFO)
        update.message.reply_text('Payment was not complete')
        context.job.schedule_removal()


def get_key_command(update: Update, context: CallbackContext) -> None:

    context.user_data['timer_count'] = 2

    context.job_queue.run_repeating(payment_check_cycle, context=(update, context.user_data), interval=3, first=1)

    text = f'xPub key: "TEST_KEY"\n'

    text += 'Waiting for payment'
    update.message.reply_text(text)


def get_data_command(update: Update, context: CallbackContext) -> None:
    if context.user_data["token"] < 1:
        update.message.reply_text(f'Not anough tokens ({context.user_data["token"]}) to perform task.')
    else:
        if context.args:
            arg = context.args[0]
            with sqlite3.connect('sqlite3.db') as con:
                cur = con.cursor()

                query = f''' 
                    SELECT name, phone_number FROM users
                    WHERE name = "{arg}" or phone_number = "{arg}"
                '''

                cur.execute(query)
                rows = cur.fetchall()

            ret_str = f'Searched:\n\t{arg}\nResults:\n'

            for row in rows:
                ret_str += f'\t{row[0]} {row[1]}\n'

            context.user_data["token"] -= 1

            ret_str += f'Tokens: {context.user_data["token"]}'

            update.message.reply_text(ret_str)
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