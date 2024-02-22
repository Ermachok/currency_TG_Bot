import json


def find_description(value: str, key: str = 'id',  description_path: str = 'currencies_descriptions.json'):
    with open(description_path) as currency_descrip_file:
        currencies_data = json.load(currency_descrip_file)

    for dictionary in currencies_data:
        if key in dictionary and dictionary[key] == value:
            return dictionary['description']
    return '{} no info'.format(value)


