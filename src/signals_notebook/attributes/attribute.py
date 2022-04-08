from typing import cast, List, Literal

from pydantic import BaseModel

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import AttrID, Response, ResponseData


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
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), id),
        )

        result = Response[cls](**response.json())

        return cast(ResponseData, result.data).body

    def __call__(self, value: str) -> str:
        if not value in self.options:
            raise ValueError('Incorrect attribute value')

        return value
