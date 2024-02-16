from typing import Dict

import requests


def _make_response(url: str, headers: Dict, params: Dict,
                   timeout: int, success=200):
    response = requests.request(url,
                                headers=headers,
                                params=params,
                                timeout=timeout)

    status_code = response.status_code

    if status_code == success:
        return response

    return status_code


def _get_currency_list(url: str, headers: Dict, head_params: Dict, timeout: int,
                       req_params: str = 'listquotes', func=_make_response):

    url = "{0}/{1}".format(url, req_params)

    response = func(url, headers=headers, params=head_params, timeout=timeout)

    return response


def _get_course(url: str, headers: Dict, head_params: Dict, req_params: Dict,
                       timeout: int, func=_make_response):

    url = "{0}/{1}/{2}".format(url, req_params['from'], req_params['to'])

    response = func(url,
                    headers=headers,
                    params=head_params,
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
