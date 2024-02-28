import json
from typing import Dict

import telebot
from telebot import types
from settings import BotSettings
from site_API.siteAPI_core import headers, site_api, url
from tg_API.utils.additional_functions import find_description, database_format, make_callback_buttons, high_low_handler

from database.common.models import db, History
from database.core import crud

from tg_API.utils.flags import BotFlags

db_write = crud.create()
db_read = crud.retrieve()

bot_settings = BotSettings()
bot = telebot.TeleBot(bot_settings.bot_token.get_secret_value())

bot_flags = BotFlags()


def exchangeRate_handler(call: types.CallbackQuery, user_getExange: Dict) -> None:
    """
    Handle exchangerate callback button.
    :param call: call from callback button in chat
    :param user_getExange: dict with keys "from" and 'to', values - currencies
    :return: none
    """
    current_currency = json.loads(call.data)['currency']
    if user_getExange[call.message.chat.username]['from'] is None:
        user_getExange[call.message.chat.username]['from'] = current_currency

        currencies_list = site_api.get_currency_list()
        response = currencies_list(url, headers, timeout=3)
        response.remove(current_currency)

        keyboard = types.InlineKeyboardMarkup(row_width=3)
        callback_buttons = make_callback_buttons(response=response,
                                                 func_name=exchangerate.__name__)

        keyboard.add(*callback_buttons)
        bot.send_message(call.message.chat.id, r"You've chosen {}. Choose second currency".format(current_currency))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      reply_markup=keyboard)

    else:
        user_getExange[call.message.chat.username]['to'] = current_currency

        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)

        exchange = site_api.get_course()
        response = exchange(url, headers, user_getExange[call.message.chat.username], timeout=3)

        bot.send_message(call.message.chat.id, "1 {cur_from} = {rate} {cur_to}".format(
            cur_from=user_getExange[call.message.chat.username]['from'],
            rate=response,
            cur_to=user_getExange[call.message.chat.username]['to']))

        db_write(db, History, database_format(user_name=call.message.chat.username,
                                              request='get_exchange',
                                              userBot_data=user_getExange[call.message.chat.username],
                                              answer=response))

        user_getExange[call.message.chat.username] = {'from': None, 'to': None}


@bot.message_handler(commands=['start'])
def start_func(message: types.Message) -> None:
    """
    Handles command start, sends list of available commands
    :param message: message from telegram api
    :return:
    """
    bot.send_message(message.chat.id, text=f'Hello, {message.from_user.username}!'
                                           f'\nI can give you a exchange rates.'
                                           f'\n\nUse command <i>/currencies</i> to see the list of available currencies.'
                                           f'\nUse command <i>/exchangerate</i> to get the exchange rate.'
                                           f'\nUse command <i>/high</i> to get the most valuable currencies relative to chosen one.'
                                           f'\nUse command <i>/low</i> to get the most valuable currencies relative to chosen one.'
                                           f'\nUse command <i>/history</i> to see history of your requests.',
                     parse_mode='HTML')


@bot.message_handler(commands=['currencies'])
def get_currencies_list(message: types.Message) -> None:
    """
    Handles command "currencies" and gives list of available ones
    :param message: message from telegram api
    :return:
    """
    currency_list = site_api.get_currency_list()
    response = currency_list(url, headers, timeout=3)
    answ_message = '\n'.join(find_description(currency) for currency in response)
    bot.send_message(message.chat.id, answ_message)

    db_dict = database_format(user_name=message.from_user.username, request=get_currencies_list.__name__,
                              answer=response)
    db_write(db, History, db_dict)


@bot.message_handler(commands=['exchangerate'])
def exchangerate(message: types.Message) -> None:
    """
    Handle exchangerate command
    :param message: message from telegram api
    :return:
    """

    bot_flags.user_getExange[message.from_user.username] = {'from': None,
                                                            'to': None}

    currencies_list = site_api.get_currency_list()
    response = currencies_list(url, headers, timeout=3)

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    callback_buttons = make_callback_buttons(response=response,
                                             func_name=exchangerate.__name__)

    keyboard.add(*callback_buttons)
    bot.send_message(message.chat.id, "Choose currencies from table below", reply_markup=keyboard)


@bot.message_handler(commands=['high'])
def higher_rates(message: types.Message) -> None:
    """
    Handles high command, provides chosen number of the most valuable currencies relative to chosen one
    :param message:
    :return:
    """

    currencies_list = site_api.get_currency_list()
    response = currencies_list(url, headers, timeout=3)

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    callback_buttons = make_callback_buttons(response=response,
                                             func_name=higher_rates.__name__)

    keyboard.add(*callback_buttons)
    bot.send_message(message.chat.id, "This command allows you to see "
                                      "the most valuable  currencies in relation to the selected one"
                                      "\nChoose currency from table below", reply_markup=keyboard)
    bot_flags.highest = True


@bot.message_handler(commands=['low'])
def lower_rates(message: types.Message) -> None:
    """
    Handles low command, provides chosen number of less valuable currencies relative to chosen one
    :param message: message from telegram api
    :return:
    """

    currencies_list = site_api.get_currency_list()
    response = currencies_list(url, headers, timeout=3)

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    callback_buttons = make_callback_buttons(response=response,
                                             func_name=higher_rates.__name__)

    keyboard.add(*callback_buttons)
    bot.send_message(message.chat.id, "This command allows you to see "
                                      "the less valuable  currencies in relation to the selected one"
                                      "\nChoose currency from table below", reply_markup=keyboard)
    bot_flags.lowest = True


@bot.message_handler(commands=['history'])
def history(message: types.Message) -> None:
    """
    Handle command history, sends history of requests of user to chat
    :param message: message from telegram api
    :return:
    """
    result = db_read(db, History, History.name, History.request, History.created_date).where(
        History.name == message.from_user.username)

    answer = ''
    for row in result:
        answer += '\nDate: {}, User: {}, Request: {}'.format(row.created_date, row.name, row.request)
    bot.send_message(message.chat.id, answer)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: types.CallbackQuery) -> None:
    """
    Handles InlineKeyboardButtons pressing
    :param call: call from  InlineKeyboardButton in chat
    :return:
    """
    # global user_getExange, ignore_text_messages, working_currency

    if call.message:
        func_name = json.loads(call.data)['func_name']
        if func_name == 'exchangerate':
            exchangeRate_handler(call, bot_flags.user_getExange)
        elif func_name == 'higher_rates':

            bot.delete_message(chat_id=call.message.chat.id,
                               message_id=call.message.message_id)
            bot_flags.working_currency = json.loads(call.data)['currency']
            bot.send_message(call.message.chat.id, "You've chosen {}".format(bot_flags.working_currency))
            bot.send_message(call.message.chat.id, "Send number of compared currencies (number < 19)")

            bot_flags.ignore_text_messages = False

        elif func_name == 'lower_rates':
            bot.delete_message(chat_id=call.message.chat.id,
                               message_id=call.message.message_id)
            bot_flags.working_currency = json.loads(call.data)['currency']
            bot.send_message(call.message.chat.id, "You've chosen {}".format(bot_flags.working_currency))
            bot.send_message(call.message.chat.id, "Send number of compared currencies (number < 19)")

            bot_flags.ignore_text_messages = False


@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message: types.Message) -> None:
    """
    Handles number from user during request of number of currencies
    :param message: message from telegram api
    :return:
    """

    if bot_flags.is_working:
        bot.reply_to(message, 'Busy at this moment')
        return

    if bot_flags.ignore_text_messages:
        bot.send_message(message.chat.id, "Use commands to interact with the bot")
    else:
        bot_flags.ignore_text_messages = True
        currency_list = site_api.get_currency_list()
        response_currencies = currency_list(url, headers, timeout=3)

        try:
            if int(message.text) > len(response_currencies):
                bot.send_message(message.chat.id, 'Wrong format (number too big)')
            else:
                bot.send_chat_action(message.chat.id, 'typing')
                bot.reply_to(message, "Working on it...")

                bot_flags.is_working = True

                if bot_flags.highest:
                    response_str, response_list = high_low_handler(bot_flags.working_currency, int(message.text),
                                                                   response_currencies, highest=True)
                    db_dict = database_format(user_name=message.from_user.username,
                                              request='get_highest', answer=response_list)
                    db_write(db, History, db_dict)
                    bot_flags.highest = False
                    bot.send_message(message.chat.id, response_str)

                elif bot_flags.lowest:
                    response_str, response_list = high_low_handler(bot_flags.working_currency, int(message.text),
                                                                   response_currencies, lowest=True)
                    bot_flags.lowest = False
                    db_dict = database_format(user_name=message.from_user.username,
                                              request='get_lowest', answer=response_list)
                    db_write(db, History, db_dict)
                    bot.send_message(message.chat.id, response_str)

                bot_flags.is_working = False

        except Exception:
            bot.send_message(message.chat.id, 'Wrong format. Start again')


def run_bot():
    bot.polling(non_stop=True)


if __name__ == '__main__':
    run_bot()
