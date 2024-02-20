import telebot
from telebot import types
from settings import BotSettings
from site_API.siteAPI_core import headers, site_api, url
from database.common.models import db, History
from database.core import crud

bot_settings = BotSettings()

bot = telebot.TeleBot(bot_settings.bot_token.get_secret_value())


@bot.message_handler(commands=['start'])
def start_func(message):
    bot.send_message(message.chat.id, text=f'Hello, {message.from_user.username}!'
                                           f'\nI can give a exchange rate')


@bot.message_handler(commands=['currencies'])
def get_currencies_list(message):
    currency_list = site_api.get_currency_list()
    response = currency_list(url, headers, timeout=3)
    bot.send_message(message.chat.id, response.json)



@bot.message_handler(commands=['exchangerate'])
def get_course(message):
    currencies_list = site_api.get_currency_list()
    response = currencies_list(url, headers, timeout=3)

    buttons = []
    for currency in response:
        buttons.append(
            [types.InlineKeyboardButton(text=currency)]
        )

    keyboard = types.InlineKeyboardMarkup(buttons)
    bot.send_message(message.chat.id, 'sfsdf', reply_markup = keyboard)


bot.polling(none_stop=True)