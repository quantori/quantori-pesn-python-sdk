from typing import Any, Dict, IO, Iterable, Mapping, Optional, Sequence, Tuple, Union

import requests

from signals_notebook.exceptions import SignalsNotebookError

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
        session = requests.Session()
        session.headers.update({'x-api-key': api_key})

        api = cls(session)
        cls.set_default_api(api)

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
            raise AttributeError('You must initialize API before using')
        return cls._default_api_instance

    def call(
        self,
        method: str,
        path: Union[str, Sequence[str]],
        params: Dict[str, Any] = None,
        data: _Data = None,
        json: Dict[str, Any] = None,
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
            raise SignalsNotebookError(response)

        return response

    @classmethod
    def _prepare_path(cls, path: Union[str, Sequence[str]]) -> str:
        if not isinstance(path, str):
            return '/'.join((cls._api_host, cls.BASE_PATH, cls.API_VERSION, *path))

        return path
