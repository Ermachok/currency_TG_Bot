from typing import Dict

import requests


def _make_response(url: str, headers: Dict, timeout: int, params: Dict = None, success=200):
    response = requests.request(method='GET',
                                url=url,
                                headers=headers,
                                params=params,
                                timeout=timeout)

    status_code = response.status_code

    if status_code == success:
        return response

    return status_code


def _get_currency_list(url: str,
                       headers: Dict,
                       timeout: int,
                       func=_make_response):
    url = "{0}/{1}".format(url, 'listquotes')
    response = func(url, headers=headers, timeout=timeout)

    return response


def _get_course(url: str, headers: Dict, params: Dict, timeout: int, func=_make_response):
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
        return _get_course


if __name__ == "__main__":
    _make_response()
    _get_currency_list()
    _get_course()

    SiteApiInterface()
