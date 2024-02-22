import json

import telebot
from telebot import types
from settings import BotSettings
from site_API.siteAPI_core import headers, site_api, url
from additional_functions import find_description
from database.common.models import db, History
from database.core import crud




bot_settings = BotSettings()
bot = telebot.TeleBot(bot_settings.bot_token.get_secret_value())

user_getExange = []

@bot.message_handler(commands=['start'])
def start_func(message):
    bot.send_message(message.chat.id, text=f'Hello, {message.from_user.username}!'
                                           f'\nI can give a exchange rate')


@bot.message_handler(commands=['currencies'])
def get_currencies_list(message):
    currency_list = site_api.get_currency_list()
    response = currency_list(url, headers, timeout=3)
    answ_message = '\n'.join(find_description(currency) for currency in response)
    bot.send_message(message.chat.id, answ_message)



@bot.message_handler(commands=['exchangerate'])
def exchangerate(message):
    user_getExange = []
    currencies_list = site_api.get_currency_list()
    response = currencies_list(url, headers, timeout=3)

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    callback_buttons = [types.InlineKeyboardButton(text='{}'.format(currency),
                                                   callback_data='{}'.format(currency)) for currency in response]
    keyboard.add(*callback_buttons)
    bot.send_message(message.chat.id, "Choose from what currency", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        user_getExange.append(call.data)
        if len(user_getExange) == 2:
            bot.send_message(call.message.chat.id, " Rabotaem brat'ya")

        elif len(user_getExange) < 2:
            currencies_list = site_api.get_currency_list()
            response = currencies_list(url, headers, timeout=3)
            response.remove(call.data)

            keyboard = types.InlineKeyboardMarkup(row_width=3)
            callback_buttons = [types.InlineKeyboardButton(text='{}'.format(currency),
                                                           callback_data='{}'.format(currency)) for currency in response]
            keyboard.add(*callback_buttons)
            bot.send_message(call.message.chat.id, "You chose {}".format(call.data))
            bot.send_message(call.message.chat.id, "Choose to what currency", reply_markup=keyboard)
        elif len(user_getExange) > 2:
            raise Exception('Something wrong')

bot.polling(none_stop=True)