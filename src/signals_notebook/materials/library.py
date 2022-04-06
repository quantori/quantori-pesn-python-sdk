from datetime import datetime
from typing import cast, List, Literal

from pydantic import BaseModel, Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.materials.asset import Asset
from signals_notebook.materials.base_entity import BaseMaterialEntity
from signals_notebook.materials.batch import Batch
from signals_notebook.types import Links, MaterialType, MID, Response, ResponseData


class ChangeBlameRecord(BaseModel):
    links: Links


class ChangeRecord(BaseModel):
    at: datetime = Field(allow_mutation=False)
    by: ChangeBlameRecord = Field(allow_mutation=False)

    class Config:
        validate_assignment = True


class _LibraryListData(BaseModel):
    id: str = Field(allow_mutation=False)
    name: str = Field(title='Name')
    digest: str = Field(allow_mutation=False, default=None)
    edited: ChangeRecord = Field(allow_mutation=False)
    created: ChangeRecord = Field(allow_mutation=False)

    class Config:
        validate_assignment = True


class LibraryListResponse(Response[_LibraryListData]):
    pass


class AssetResponse(Response[Asset]):
    pass


class BatchResponse(Response[Batch]):
    pass


class Library(BaseMaterialEntity):
    type: Literal[MaterialType.LIBRARY] = Field(allow_mutation=False, default=MaterialType.LIBRARY)

    class Config:
        validate_assignment = True

    @classmethod
    def get_list(cls) -> List['Library']:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), 'libraries'),
        )

        result = LibraryListResponse(**response.json())

        libraries: List['Library'] = []
        for item in result.data:
            data = cast(_LibraryListData, cast(ResponseData, item).body)
            libraries.append(
                cls(
                    assetTypeId=data.id,
                    eid=MID(f'{MaterialType.LIBRARY}:{data.id}'),
                    library=data.name,
                    name=data.name,
                    digest=data.digest.split(':')[0],
                    createdAt=data.created.at,
                    editedAt=data.edited.at,
                )
            )

        return libraries

    def get_asset(self, name: str) -> Asset:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.name, 'assets', 'id', name),
        )

        result = AssetResponse(**response.json())

        return cast(ResponseData, result.data).body

    def get_asset_batches(self, name: str) -> List[Batch]:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.name, 'assets', name, 'batches'),
        )

        result = BatchResponse(**response.json())

        return [cast(ResponseData, item).body for item in result.data]

    def get_batch(self, name: str) -> Batch:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.name, 'batches', 'id', name),
        )

        result = BatchResponse(**response.json())

        return cast(ResponseData, result.data).body
