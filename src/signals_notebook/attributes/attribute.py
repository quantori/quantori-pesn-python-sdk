import logging
from typing import cast, Optional, Literal, Generator

from pydantic import BaseModel

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import AttrID, Response, ResponseData

log = logging.getLogger(__name__)


class Attribute(BaseModel):
    type: Literal['choice', 'attribute']
    id: AttrID
    name: str
    options: Optional[list[str]]

    class Meta:
        frozen = True

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'attributes'

    @classmethod
    def get(cls, id: AttrID) -> 'Attribute':
        """Get Attribute object by id

        Args:
            id: AttrID

        Returns:
            Attribute
        """
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), id),
        )

        result = Response[cls](**response.json())  # type: ignore
        log.debug('Get Attribute with ID: %s', id)

        return cast(ResponseData, result.data).body

    @classmethod
    def get_list(
        cls,
    ) -> Generator['Attribute', None, None]:
        """Get all Attributes.

        Returns:
            Generator
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get List of Attributes')

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(),),
        )
        result = Response[cls](**response.json())  # type: ignore

        yield from [cast(ResponseData, item).body for item in result.data]

        while result.links and result.links.next:
            response = api.call(
                method='GET',
                path=result.links.next,
            )

            result = Response[cls](**response.json())  # type: ignore
            yield from [cast(ResponseData, item).body for item in result.data]

        log.debug('List of Attributes was got successfully.')

    def __call__(self, value: str) -> str:
        if value not in self.options:
            log.exception('Incorrect attribute value')
            raise ValueError('Incorrect attribute value')

        return value
