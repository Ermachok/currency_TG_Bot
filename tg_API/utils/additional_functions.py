import json
from typing import Dict, AnyStr


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
               'exchange_rate': exchange
               }
    return db_dict
