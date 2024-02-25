import json

import telebot
from telebot import types
from settings import BotSettings
from site_API.siteAPI_core import headers, site_api, url
from tg_API.utils.additional_functions import find_description, database_format, make_callback_buttons, high_low_handler
from database.common.models import db, History
from database.core import crud


db_write = crud.create()
db_read = crud.retrieve()

bot_settings = BotSettings()
bot = telebot.TeleBot(bot_settings.bot_token.get_secret_value())

user_getExange = {}
working_currency = ''

ignore_text_messages = True
is_working = False

highest = False
lowest = False


def exchangeRate_handler(call, user_getExange):
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
                                              userBot_data=user_getExange[call.message.chat.username],
                                              exchange=response))

        user_getExange[call.message.chat.username] = {'from': None, 'to': None}


@bot.message_handler(commands=['start'])
def start_func(message):
    bot.send_message(message.chat.id, text=f'Hello, {message.from_user.username}!'
                                           f'\nI can give you a exchange rates.'
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
    callback_buttons = make_callback_buttons(response=response,
                                             func_name=exchangerate.__name__)

    keyboard.add(*callback_buttons)
    bot.send_message(message.chat.id, "Choose currencies from table below", reply_markup=keyboard)


@bot.message_handler(commands=['high'])
def higher_rates(message):
    global highest

    currencies_list = site_api.get_currency_list()
    response = currencies_list(url, headers, timeout=3)

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    callback_buttons = make_callback_buttons(response=response,
                                             func_name=higher_rates.__name__)

    keyboard.add(*callback_buttons)
    bot.send_message(message.chat.id, "This command allows you to see "
                                      "the most valuable  currencies in relation to the selected one"
                                      "\nChoose currency from table below", reply_markup=keyboard)
    highest = True


@bot.message_handler(commands=['low'])
def lower_rates(message):
    global lowest

    currencies_list = site_api.get_currency_list()
    response = currencies_list(url, headers, timeout=3)

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    callback_buttons = make_callback_buttons(response=response,
                                             func_name=higher_rates.__name__)

    keyboard.add(*callback_buttons)
    bot.send_message(message.chat.id, "This command allows you to see "
                                      "the less valuable  currencies in relation to the selected one"
                                      "\nChoose currency from table below", reply_markup=keyboard)
    lowest = True


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global user_getExange, ignore_text_messages, working_currency

    if call.message:
        func_name = json.loads(call.data)['func_name']
        if func_name == 'exchangerate':
            exchangeRate_handler(call, user_getExange)
        elif func_name == 'high_rates':

            bot.delete_message(chat_id=call.message.chat.id,
                               message_id=call.message.message_id)
            working_currency = json.loads(call.data)['currency']
            bot.send_message(call.message.chat.id, "You've chosen {}".format(working_currency))
            bot.send_message(call.message.chat.id, "Send number of compared currencies (number < 19)")

            ignore_text_messages = False

        elif func_name == 'low_rates':
            bot.delete_message(chat_id=call.message.chat.id,
                               message_id=call.message.message_id)
            working_currency = json.loads(call.data)['currency']
            bot.send_message(call.message.chat.id, "You've chosen {}".format(working_currency))
            bot.send_message(call.message.chat.id, "Send number of compared currencies (number < 19)")

            ignore_text_messages = False


@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    global highest, lowest, is_working, working_currency, ignore_text_messages

    if is_working:
        bot.reply_to(message, 'Busy at this moment')
        return

    if ignore_text_messages:
        bot.send_message(message.chat.id, "Use commands to interact with the bot")
    else:
        ignore_text_messages = True
        currency_list = site_api.get_currency_list()
        response = currency_list(url, headers, timeout=3)

        try:
            if int(message.text) > len(response):
                bot.send_message(message.chat.id, 'Wrong format (number too big)')
            else:
                bot.send_chat_action(message.chat.id, 'typing')
                bot.reply_to(message, "Working on it...")

                is_working = True

                if highest:
                    response = high_low_handler(working_currency, int(message.text), response, highest=True)
                    highest = False
                elif lowest:
                    response = high_low_handler(working_currency, int(message.text), response, lowest=True)
                    lowest = False

                bot.send_message(message.chat.id, response)
                is_working = False

        except Exception:
            bot.send_message(message.chat.id, 'Wrong format. Start again')



def run_bot():
    bot.polling(non_stop=True)


if __name__ == '__main__':
    run_bot()