import json
from typing import Dict, AnyStr, List
from telebot import types

from site_API.siteAPI_core import headers, site_api, url


def find_description(value: AnyStr, key: AnyStr = 'id',
                     description_path: AnyStr = 'tg_API/utils/currencies_descriptions.json') -> AnyStr:
    """
    Returns string with value description
    :param value: currency name
    :param key: key in description file
    :param description_path: path to values descriptions
    :return: description of currency
    """
    with open(description_path) as currency_descrip_file:
        currencies_data = json.load(currency_descrip_file)

    for dictionary in currencies_data:
        if key in dictionary and dictionary[key] == value:
            return dictionary['description']
    return '{} no info'.format(value)


def database_format(user_name: AnyStr, request, answer: AnyStr, userBot_data=None) -> Dict:
    """
    Makes from data format for writing in database
    :param user_name: username from chat
    :param request: request name
    :param answer: answer from request
    :param userBot_data: in case of exchange rate command, contain keys "from" and "to"
    :return: dict ready for writing in db
    """
    if userBot_data is None:
        userBot_data = {'from': '', 'to': ''}
    db_dict = {'name': user_name,
               'request': request,
               'from_currency': userBot_data['from'],
               'to_currency': userBot_data['to'],
               'answer': answer
               }
    return db_dict


def make_callback_buttons(response: List, func_name: AnyStr) -> List[types.InlineKeyboardButton]:
    """
    Generate list of InlineKeyboardButtons with required data in callback
    :param response: answer of currencies list request
    :param func_name: command which triggers appearing of callback
    :return: list of InlineKeyboardButtons
    """
    buttons = [types.InlineKeyboardButton(text='{}'.format(currency),
                                          callback_data=json.dumps({'func_name': func_name,
                                                                    'currency': currency})) for currency in response]
    return buttons


def high_low_handler(working_cur: AnyStr, currencies_number: int, currencies_list: List,
                     highest: bool = False, lowest: bool = False) -> (AnyStr, List):
    """
    Handles commans high/low
    :param working_cur: currency against which the rates are based
    :param currencies_number: number of currencies in response
    :param currencies_list: list of all available currencies
    :param highest: marker of regime in which function is working
    :param lowest: marker of regime in which function is working
    :return: string for response in chat and list for writing in databqse
    """
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

    response_str = '1 {} equals:'.format(working_cur)
    for cur in range(currencies_number):
        response_str = response_str + '\n{} {}'.format(result_list[cur]['exchange_rate'],
                                                       result_list[cur]['currency'])

    return response_str, result_list[:currencies_number]
