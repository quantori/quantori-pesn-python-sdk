import logging
from typing import cast, List, Literal

from pydantic import BaseModel

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import AttrID, Response, ResponseData

log = logging.getLogger(__name__)


class Attribute(BaseModel):
    type: Literal['choice']
    id: AttrID
    name: str
    options: List[str]

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

    def __call__(self, value: str) -> str:
        if value not in self.options:
            log.exception('Incorrect attribute value')
            raise ValueError('Incorrect attribute value')

        return value
