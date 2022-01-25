from typing import Any, BinaryIO, Dict

import requests


class SignalsNotebookApi:

    _default_api = None

    def __init__(self, session: requests.Session):
        self._session = session

    @classmethod
    def init(cls, api_key: str) -> 'SignalsNotebookApi':
        session = requests.Session()
        session.headers.update({'x-api-key': api_key})

        api = cls(session)

        return api

    @classmethod
    def set_default_api(cls, api: 'SignalsNotebookApi') -> None:
        cls._default_api = api

    @classmethod
    def get_default_api(cls) -> 'SignalsNotebookApi':
        return cls._default_api

    def call(
        self,
        method: str,
        path: str,
        params: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        files: Dict[str, BinaryIO] = None,
    ) -> requests.Response:
        """
        Makes an API call
        :param method: The HTTP method name (e.g. 'GET').
        :param path: an absolute API path
        :param params: (optional) A mapping of request parameters where a key
                is the parameter name and its value is a string or an object
                which can be JSON-encoded.
        :param headers: (optional) A mapping of request headers where a key is the
                header name and its value is the header value.
        :param files: (optional) An optional mapping of file names to binary open
                file objects. These files will be attached to the request.
        :return: a response object
        """

        if not params:
            params = {}
        if not headers:
            headers = {}
        if not files:
            files = {}

        request_params = {
            'method': method,
            'path': path,
            'headers': headers,
            'files': files,
        }

        if method in ('GET', 'DELETE'):
            request_params['params'] = params
        else:
            request_params['data'] = params

        response = self._session.request(**request_params)
        response.raise_for_status()

        return response
