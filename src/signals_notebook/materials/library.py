from datetime import datetime
from typing import cast, List, Literal, Optional

from pydantic import BaseModel, Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import Links, MaterialType, MID, Response, ResponseData
from signals_notebook.materials.asset import Asset
from signals_notebook.materials.base_entity import BaseMaterialEntity
from signals_notebook.materials.batch import Batch
from signals_notebook.materials.field import GenericField


class ChangeBlameRecord(BaseModel):
    links: Links


class ChangeRecord(BaseModel):
    at: datetime = Field(allow_mutation=False)
    by: ChangeBlameRecord = Field(allow_mutation=False)

    class Config:
        validate_assignment = True


class Numbering(BaseModel):
    format: str


class AssetConfig(BaseModel):
    asset_name_field_id: Optional[str] = Field(alias='assetNameFieldId', default=None)
    display_name: str = Field(alias='displayName')
    numbering: Numbering
    fields: List[GenericField]


class _LibraryListData(BaseModel):
    id: str = Field(allow_mutation=False)
    name: str = Field(title='Name')
    digest: str = Field(allow_mutation=False, default=None)
    edited: ChangeRecord = Field(allow_mutation=False)
    created: ChangeRecord = Field(allow_mutation=False)
    asset_config: AssetConfig = Field(alias='assets')

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
    _asset_config: Optional[AssetConfig] = PrivateAttr(default=None)

    class Config:
        validate_assignment = True

    @property
    def asset_config(self) -> AssetConfig:
        if self._asset_config:
            return self._asset_config

        # the only way to get config is to fetch all libraries
        result = self._get_library_list_response()
        for item in result.data:
            data = cast(_LibraryListData, cast(ResponseData, item).body)
            if data.id == self.asset_type_id:
                self._asset_config = data.asset_config
                break

        assert self._asset_config is not None
        return self._asset_config

    @asset_config.setter
    def asset_config(self, config: AssetConfig) -> None:
        self._asset_config = config

    @classmethod
    def _get_library_list_response(cls) -> LibraryListResponse:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), 'libraries'),
        )

        return LibraryListResponse(**response.json())

    @classmethod
    def get_list(cls) -> List['Library']:
        result = cls._get_library_list_response()

        libraries: List['Library'] = []
        for item in result.data:
            data = cast(_LibraryListData, cast(ResponseData, item).body)
            library = cls(
                asset_type_id=data.id,
                eid=MID(f'{MaterialType.LIBRARY}:{data.id}'),
                library_name=data.name,
                name=data.name,
                digest=data.digest.split(':')[0],
                created_at=data.created.at,
                edited_at=data.edited.at,
            )
            library.asset_config = data.asset_config
            libraries.append(library)

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
