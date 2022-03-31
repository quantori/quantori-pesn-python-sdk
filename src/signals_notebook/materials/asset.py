from typing import cast, Generator, Literal

from pydantic import Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.materials.batch import Batch
from signals_notebook.materials.material import Material
from signals_notebook.types import MaterialType, Response, ResponseData


class BatchesListResponse(Response[Batch]):
    pass


class Asset(Material):
    type: Literal[MaterialType.ASSET] = Field(allow_mutation=False, default=MaterialType.ASSET)

    def get_batches(self) -> Generator[Batch, None, None]:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.library, 'assets', self.name, 'batches'),
        )

        result = BatchesListResponse(**response.json())
        yield from [cast(ResponseData, item).body for item in result.data]

        while result.links.next:
            response = api.call(
                method='GET',
                path=result.links.next,
            )

            result = BatchesListResponse(**response.json())
            yield from [cast(ResponseData, item).body for item in result.data]
