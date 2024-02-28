from typing import Dict, AnyStr, Callable

import requests


def _make_response(url: AnyStr,
                   headers: Dict,
                   timeout: int,
                   params: Dict = None,
                   success: int = 200) -> Dict:
    """
    Gives response from url
    :param url: site url
    :param headers: headers
    :param timeout: time to wait response
    :param params: parameters for request
    :param success: success status, int
    :return:
    """
    response = requests.request(method='GET',
                                url=url,
                                headers=headers,
                                params=params,
                                timeout=timeout)

    status_code = response.status_code

    if status_code == success:
        return response.json()

    return {'response': status_code}


def _get_currency_list(url: AnyStr,
                       headers: Dict,
                       timeout: int,
                       func=_make_response) -> Dict:
    """
    Gives list of available currencies
    :param url:api url
    :param headers: headers
    :param timeout: time to wait response
    :param func: func with request
    :return: currencies list
    """

    url = "{0}/{1}".format(url, 'listquotes')
    response = func(url, headers=headers, timeout=timeout)

    return response


def _get_exchange(url: AnyStr,
                  headers: Dict,
                  params: Dict,
                  timeout: int,
                  func: Callable = _make_response) -> Dict:
    """
    Gives exchange rate of 2 currencies
    :param url:  api url
    :param headers: headers
    :param params: dict with keys "from" and "to"
    :param timeout: time to wait response
    :param func: general request func
    :return: response from site api
    """
    url = "{0}/{1}".format(url, 'exchange')

    querystring = {'from': '{}'.format(params['from']),
                   'to': '{}'.format(params['to']),
                   'q': '1.0'}

    response = func(url,
                    headers=headers,
                    params=querystring,
                    timeout=timeout)

    return response


class SiteApiInterface():

    @staticmethod
    def get_currency_list():
        return _get_currency_list

    @staticmethod
    def get_course():
        return _get_exchange


if __name__ == "__main__":
    _make_response()
    _get_currency_list()
    _get_exchange()

    SiteApiInterface()
