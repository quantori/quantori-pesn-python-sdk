from datetime import datetime
from typing import cast, List, Literal, Optional

from pydantic import BaseModel, Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import Links, MaterialType, MID, Response, ResponseData
from signals_notebook.materials.asset import Asset
from signals_notebook.materials.base_entity import BaseMaterialEntity
from signals_notebook.materials.batch import Batch
from signals_notebook.materials.field import AssetConfig, BatchConfig


class ChangeBlameRecord(BaseModel):
    links: Links


class ChangeRecord(BaseModel):
    at: datetime = Field(allow_mutation=False)
    by: ChangeBlameRecord = Field(allow_mutation=False)

    class Config:
        validate_assignment = True


class _LibraryListData(BaseModel):
    id: str
    name: str
    digest: str
    edited: ChangeRecord
    created: ChangeRecord
    asset_config: AssetConfig = Field(alias='assets')
    batch_config: BatchConfig = Field(alias='batches')

    class Config:
        frozen = True


class LibraryListResponse(Response[_LibraryListData]):
    pass


class AssetResponse(Response[Asset]):
    pass


class BatchResponse(Response[Batch]):
    pass


class Library(BaseMaterialEntity):
    type: Literal[MaterialType.LIBRARY] = Field(allow_mutation=False, default=MaterialType.LIBRARY)
    _asset_config: Optional[AssetConfig] = PrivateAttr(default=None)
    _batch_config: Optional[BatchConfig] = PrivateAttr(default=None)

    class Config:
        validate_assignment = True

    def _load_configs(self) -> None:
        # the only way to get config is to fetch all libraries
        result = self._get_library_list_response()
        for item in result.data:
            data = cast(_LibraryListData, cast(ResponseData, item).body)
            if data.id == self.asset_type_id:
                self._asset_config = data.asset_config
                self._batch_config = data.batch_config
                return

    @property
    def asset_config(self) -> AssetConfig:
        if self._asset_config:
            return self._asset_config

        self._load_configs()

        assert self._asset_config is not None
        return self._asset_config

    @asset_config.setter
    def asset_config(self, config: AssetConfig) -> None:
        self._asset_config = config

    @property
    def batch_config(self) -> BatchConfig:
        if self._batch_config:
            return self._batch_config

        self._load_configs()

        assert self._batch_config is not None
        return self._batch_config

    @batch_config.setter
    def batch_config(self, config: BatchConfig) -> None:
        self._batch_config = config

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
            # library.batch_config = data.batch_config
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
