import json

import telebot
from telebot import types
from settings import BotSettings
from site_API.siteAPI_core import headers, site_api, url
from tg_API.utils.additional_functions import find_description
from database.common.models import db, History
from database.core import crud




bot_settings = BotSettings()
bot = telebot.TeleBot(bot_settings.bot_token.get_secret_value())

user_getExange = {}


@bot.message_handler(commands=['start'])
def start_func(message):
    bot.send_message(message.chat.id, text=f'Hello, {message.from_user.username}!'
                                           f'\nI can give you a exchange rate.'
                                           f'\n\nUse command <i>/currencies</i> to see the list of available currencies.'
                                           f'\nUse command <i>/exchangerate</i> to get the exchange rate.',
                                           parse_mode='HTML')


@bot.message_handler(commands=['currencies'])
def get_currencies_list(message):
    currency_list = site_api.get_currency_list()
    response = currency_list(url, headers, timeout=3)
    answ_message = '\n'.join(find_description(currency) for currency in response)
    bot.send_message(message.chat.id, answ_message)



@bot.message_handler(commands=['exchangerate'])
def exchangerate(message):
    global user_getExange
    user_getExange[message.from_user.username] = {'from': None,
                                                  'to': None}

    currencies_list = site_api.get_currency_list()
    response = currencies_list(url, headers, timeout=3)

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    callback_buttons = [types.InlineKeyboardButton(text='{}'.format(currency),
                                                   callback_data='{}'.format(currency)) for currency in response]
    keyboard.add(*callback_buttons)
    bot.send_message(message.chat.id, "Choose currencies from table below", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global user_getExange
    if call.message:
        if user_getExange[call.message.chat.username]['from'] is None:
            user_getExange[call.message.chat.username]['from'] = call.data

            currencies_list = site_api.get_currency_list()
            response = currencies_list(url, headers, timeout=3)
            response.remove(call.data)

            keyboard = types.InlineKeyboardMarkup(row_width=3)
            callback_buttons = [types.InlineKeyboardButton(text='{}'.format(currency),
                                                           callback_data='{}'.format(currency)) for currency in response]

            keyboard.add(*callback_buttons)
            bot.send_message(call.message.chat.id, r"You've chosen {}. Choose second currency".format(call.data))
            bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=keyboard)

        else:
            user_getExange[call.message.chat.username]['to'] = call.data

            bot.delete_message(chat_id=call.message.chat.id,
                               message_id=call.message.message_id)

            exchange = site_api.get_course()
            response = exchange(url, headers, user_getExange[call.message.chat.username], timeout=3)

            bot.send_message(call.message.chat.id, "Kurs {}".format(response))

            user_getExange[call.message.chat.username] = {'from': None,
                                                          'to': None}


@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    bot.send_message(message.chat.id, "Use commands to interact with the bot.")


def run_bot():
    bot.polling(non_stop=True)


if __name__ == '__main__':
    run_bot()