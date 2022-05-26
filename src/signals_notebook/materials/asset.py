from typing import Any, cast, Generator, Literal

from pydantic import Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import MaterialType, Response, ResponseData
from signals_notebook.materials.batch import Batch
from signals_notebook.materials.field import FieldContainer
from signals_notebook.materials.material import Material


class BatchesListResponse(Response[Batch]):
    pass


class Asset(Material):
    type: Literal[MaterialType.ASSET] = Field(allow_mutation=False, default=MaterialType.ASSET)

    def __init__(self, **data: Any):
        fields = data.pop('fields', {})

        super().__init__(**data)

        self._material_fields = FieldContainer(self, self.library.asset_config.fields, **fields)

    def get_batches(self) -> Generator[Batch, None, None]:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.library_name, 'assets', self.name, 'batches'),
        )

        result = BatchesListResponse(_context={'_library': self.library}, **response.json())
        yield from [cast(ResponseData, item).body for item in result.data]

        while result.links and result.links.next:
            response = api.call(
                method='GET',
                path=result.links.next,
            )

            result = BatchesListResponse(_context={'_library': self.library}, **response.json())
            yield from [cast(ResponseData, item).body for item in result.data]