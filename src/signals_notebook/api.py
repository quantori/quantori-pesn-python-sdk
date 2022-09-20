import logging
from enum import Enum
from typing import Any, Dict, IO, Iterable, Mapping, Optional, Sequence, Tuple, Union

import requests

from signals_notebook.exceptions import SignalsNotebookError

log = logging.getLogger(__name__)

_Data = Union[None, str, bytes, Mapping[str, Any], Mapping[str, Any], Iterable[Tuple[str, Optional[str]]], IO[Any]]


class SignalsNotebookApi:

    _default_api_instance = None
    _api_host = ''

    API_VERSION = 'v1.0'
    """api version. Default = "v1.0" (str)
    """
    BASE_PATH = 'api/rest'
    """api base path (str)
    """
    HTTP_DEFAULT_HEADERS = {
        'Content-Type': 'application/vnd.api+json',
    }
    """ headers that are used in api (dict)
    """

    def __init__(self, session: requests.Session):
        """
        Args:
            session: A Requests session
        """
        self._session = session

    @classmethod
    def init(cls, api_host: str, api_key: str) -> 'SignalsNotebookApi':
        """Initialize SignalsNotebookApi with api host and api key

        Args:
            api_host: api host for signals notebook api
            api_key: api key for signals notebook api

        Returns:
            SignalsNotebookApi
        """
        cls._api_host = api_host

        log.info('Initialize session for api...')
        session = requests.Session()
        log.info('Session created. session.headers: %s', session.headers)

        session.headers.update({'x-api-key': api_key})

        api = cls(session)
        cls.set_default_api(api)
        log.info(
            'Default api configured. Host: %s | Base Path: %s | Version: %s ',
            api._api_host,
            api.BASE_PATH,
            api.API_VERSION,
        )
        return api

    @classmethod
    def set_default_api(cls, api: 'SignalsNotebookApi') -> None:
        """Set default api

        Args:
            api: default api

        Returns:

        """
        cls._default_api_instance = api

    @classmethod
    def get_default_api(cls) -> 'SignalsNotebookApi':
        """Get initialized API

        Returns:
            SignalsNotebookApi: Initialized API
        """
        if not cls._default_api_instance:
            log.error('You must initialize API before using')
            raise AttributeError('You must initialize API before using')
        return cls._default_api_instance

    def call(
        self,
        method: str,
        path: Union[str, Sequence[str]],
        params: Dict[str, Any] = None,
        data: _Data = None,
        json: Union[list, Dict[str, Any]] = None,
        headers: Dict[str, str] = None,
    ) -> requests.Response:
        """Makes an API call

        Args:
            method: The HTTP method name (e.g. 'GET').
            path: an absolute API path
            params: (optional) A mapping of request parameters where a key
                is the parameter name and its value is a string or an object
                which can be JSON-encoded.
            data: (optional) Dictionary, list of tuples, bytes, or file-like
                object to send in the body of the :class:`Request`.
            json:  (optional) A request body
            headers: (optional) A mapping of request headers where a key is the
                header name and its value is the header value.

        Returns:
            Response object
        """
        if not params:
            params = {}
        if not headers:
            headers = {}

        headers = {**self.HTTP_DEFAULT_HEADERS, **headers}

        for key, value in headers.items():
            if isinstance(value, Enum):
                headers[key] = value.value

        if json:
            response = self._session.request(
                method=method,
                url=self._prepare_path(path),
                params=params,
                json=json,
                headers=headers,
            )
        elif data:
            response = self._session.request(
                method=method,
                url=self._prepare_path(path),
                params=params,
                data=data,
                headers=headers,
            )
        else:
            response = self._session.request(
                method=method,
                url=self._prepare_path(path),
                params=params,
                headers=headers,
            )
        if not response.ok:
            log.error(
                'Error has been occurred while getting response, status code: %s',
                response.status_code,
                extra={'response': response},
            )
            raise SignalsNotebookError(response)
        log.info('Successful request - HTTP url: %s, status code: %s', response.url, response.status_code)

        return response

    @classmethod
    def _prepare_path(cls, path: Union[str, Sequence[str]]) -> str:
        if not isinstance(path, str):
            return '/'.join((cls._api_host, cls.BASE_PATH, cls.API_VERSION, *path))

        return path
