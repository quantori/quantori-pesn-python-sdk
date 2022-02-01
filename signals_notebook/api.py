from collections.abc import Sequence
from typing import Any, Dict, IO, Type, Union

import requests

from signals_notebook.exceptions import SignalsNotebookError
from signals_notebook.types import EntityClass, Response


class SignalsNotebookApi:

    _default_api_instance = None
    _api_host = ''

    API_VERSION = 'v1.0'
    BASE_PATH = 'api/rest'
    HTTP_DEFAULT_HEADERS = {
        'Content-Type': 'application/vnd.api+json',
    }

    def __init__(self, session: requests.Session):
        self._session = session

    @classmethod
    def init(cls, api_host: str, api_key: str) -> 'SignalsNotebookApi':
        cls._api_host = api_host
        session = requests.Session()
        session.headers.update({'x-api-key': api_key})

        api = cls(session)
        cls.set_default_api(api)

        return api

    @classmethod
    def set_default_api(cls, api: 'SignalsNotebookApi') -> None:
        cls._default_api_instance = api

    @classmethod
    def get_default_api(cls) -> 'SignalsNotebookApi':
        if not cls._default_api_instance:
            raise AttributeError('You must initialize API before using')
        return cls._default_api_instance

    def call(
        self,
        method: str,
        path: Union[str, Sequence[str]],
        params: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        files: Dict[str, IO] = None,
        target_class: Type[EntityClass] = None,
    ) -> Response:
        """
        Makes an API call
        :param method: The HTTP method name (e.g. 'GET').
        :param path: an absolute API path
        :param params: (optional) A mapping of request parameters where a key
                is the parameter name and its value is a string or an object
                which can be JSON-encoded.
        :param data: (optional) A request body
        :param headers: (optional) A mapping of request headers where a key is the
                header name and its value is the header value.
        :param files: (optional) An optional mapping of file names to binary open
                file objects. These files will be attached to the request.
        :param target_class: a class-container for response data
        :return: a response object
        """

        if not params:
            params = {}
        if not headers:
            headers = {}
        if not files:
            files = {}

        headers.update(self.HTTP_DEFAULT_HEADERS)

        response = self._session.request(
            method=method,
            url=self._prepare_path(path),
            params=params,
            json=data,
            headers=headers,
            files=files,
        )

        if not response.ok:
            raise SignalsNotebookError(response)

        if target_class:
            result = Response[target_class](**response.json())  # type: ignore
            return result

        return None

    @classmethod
    def _prepare_path(cls, path: Union[str, Sequence[str]]) -> str:
        if not isinstance(path, str):
            return '/'.join((cls._api_host, cls.BASE_PATH, cls.API_VERSION, *path))

        return path
