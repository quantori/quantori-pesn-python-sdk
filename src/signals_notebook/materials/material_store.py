from typing import cast, Union

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.materials.library import Library
from signals_notebook.materials.material import Material
from signals_notebook.types import MID, Response, ResponseData


class MaterialResponse(Response[Union[Library]]):
    pass


class MaterialStore:

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'materials'

    @classmethod
    def get(cls, eid: MID) -> Material:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), eid),
        )

        result = MaterialResponse(**response.json())

        return cast(ResponseData, result.data).body
