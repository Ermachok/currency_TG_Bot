import json
from typing import Dict, AnyStr, List
from telebot import types

from site_API.siteAPI_core import headers, site_api, url




def find_description(value: AnyStr, key: AnyStr = 'id',
                     description_path: AnyStr = 'tg_API/utils/currencies_descriptions.json'):
    with open(description_path) as currency_descrip_file:
        currencies_data = json.load(currency_descrip_file)

    for dictionary in currencies_data:
        if key in dictionary and dictionary[key] == value:
            return dictionary['description']
    return '{} no info'.format(value)


def database_format(user_name: AnyStr, userBot_data: Dict, exchange: AnyStr) -> Dict:
    db_dict = {'name': user_name,
               'from_currency': userBot_data['from'],
               'to_currency': userBot_data['to'],
               'answer': exchange
               }
    return db_dict


def make_callback_buttons(response: List, func_name: AnyStr):
    buttons = [types.InlineKeyboardButton(text='{}'.format(currency),
                                          callback_data=json.dumps({'func_name': func_name,
                                                                    'currency': currency})) for currency in response]
    return buttons


def high_low_handler(working_cur: AnyStr, currencies_number: int, currencies_list: List,
                     highest: bool = False, lowest: bool = False) -> AnyStr:

    currencies_list.remove(working_cur)
    exchange = site_api.get_course()

    result_list = []
    for currency in currencies_list:
        response = exchange(url, headers, {'from': working_cur, 'to': currency}, timeout=3)
        result_list.append({'currency': currency, 'exchange_rate': round(float(response), 3)})

    if highest:
        result_list = sorted(result_list, key=lambda x: x['exchange_rate'])
    elif lowest:
        result_list = sorted(result_list, key=lambda x: x['exchange_rate'], reverse=True)

    response = '1 {} equals:'.format(working_cur)
    for cur in range(currencies_number):
        response = response + '\n{} {}'.format(result_list[cur]['exchange_rate'],
                                               result_list[cur]['currency'])

    return response
