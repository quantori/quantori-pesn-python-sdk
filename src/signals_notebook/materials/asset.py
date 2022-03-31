from typing import cast, Generator, Literal

from pydantic import Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.materials.library import Library
from signals_notebook.materials.batch import Batch
from signals_notebook.materials.material import Material
from signals_notebook.types import MaterialType, MID, Response, ResponseData


class BatchesListResponse(Response[Batch]):
    pass


class Asset(Material):
    type: Literal[MaterialType.ASSET] = Field(allow_mutation=False, default=MaterialType.ASSET)

    @property
    def library(self) -> Library:
        from signals_notebook.materials.material_store import MaterialStore
        library = MaterialStore.get(MID(f'{MaterialType.LIBRARY}:{self.asset_type_id}'))
        return cast(Library, library)

    def get_batches(self) -> Generator[Batch, None, None]:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.library_name, 'assets', self.name, 'batches'),
        )

        result = BatchesListResponse(**response.json())
        yield from [cast(ResponseData, item).body for item in result.data]

        while result.links and result.links.next:
            response = api.call(
                method='GET',
                path=result.links.next,
            )

            result = BatchesListResponse(**response.json())
            yield from [cast(ResponseData, item).body for item in result.data]
