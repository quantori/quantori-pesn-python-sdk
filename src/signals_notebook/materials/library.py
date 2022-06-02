import logging
from datetime import datetime
from typing import Any, cast, List, Literal, Optional, Union

from pydantic import BaseModel, Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import Links, MaterialType, MID, Response, ResponseData
from signals_notebook.materials.asset import Asset
from signals_notebook.materials.base_entity import BaseMaterialEntity
from signals_notebook.materials.batch import Batch
from signals_notebook.materials.field import AssetConfig, BatchConfig

log = logging.getLogger(__name__)


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


class BatchAssetField(BaseModel):
    id: str
    value: Any


class BatchAssetAttribute(BaseModel):
    fields: List[BatchAssetField]


class BatchRequestData(BaseModel):
    type: str = MaterialType.BATCH
    attributes: BatchAssetAttribute


class DataRelationship(BaseModel):
    data: BatchRequestData


class AssetRelationship(BaseModel):
    batch: DataRelationship


class AssetRequestData(BaseModel):
    type: str = MaterialType.ASSET
    attributes: BatchAssetAttribute
    relationships: Optional[AssetRelationship] = None


class Library(BaseMaterialEntity):
    type: Literal[MaterialType.LIBRARY] = Field(allow_mutation=False, default=MaterialType.LIBRARY)
    _asset_config: Optional[AssetConfig] = PrivateAttr(default=None)
    _batch_config: Optional[BatchConfig] = PrivateAttr(default=None)

    class Config:
        validate_assignment = True

    def _load_configs(self) -> None:
        # the only way to get config is to fetch all libraries
        log.debug('Loading asset and batch configs to %s for %s', self.__class__.__name__, self.eid)

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

        log.debug('Checking Asset Config for %s...', self.eid)
        if self._asset_config is None:
            log.warning('Asset Config for %s cannot be None', self.eid)
        assert self._asset_config is not None, f'Asset Config for {self.eid} cannot be None'
        return self._asset_config

    @asset_config.setter
    def asset_config(self, config: AssetConfig) -> None:
        self._asset_config = config

    @property
    def batch_config(self) -> BatchConfig:
        if self._batch_config:
            return self._batch_config

        self._load_configs()
        log.debug('Checking Batch Config for %s...', self.eid)
        if self._batch_config is None:
            log.warning('Batch Config for %s cannot be None', self.eid)
        assert self._asset_config is not None, f'Batch Config for {self.eid} cannot be None'
        return self._batch_config

    @batch_config.setter
    def batch_config(self, config: BatchConfig) -> None:
        self._batch_config = config

    @classmethod
    def _get_library_list_response(cls) -> LibraryListResponse:
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get Library List Response for %s', cls.__name__)

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), 'libraries'),
        )

        return LibraryListResponse(**response.json())

    @classmethod
    def get_list(cls) -> List['Library']:
        result = cls._get_library_list_response()
        log.debug('Get List of Libraries for %s', cls.__name__)

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
            library.batch_config = data.batch_config
            libraries.append(library)

        return libraries

    def get_asset(self, name: str) -> Asset:
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get Asset for %s with name: %s', self.eid, name)

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.name, 'assets', 'id', name),
        )

        result = AssetResponse(_context={'_library': self}, **response.json())

        return cast(ResponseData, result.data).body

    def get_asset_batches(self, name: str) -> List[Batch]:
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get Asset of Batches for %s with name: %s', self.eid, name)

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.name, 'assets', name, 'batches'),
        )

        result = BatchResponse(_context={'_library': self}, **response.json())

        return [cast(ResponseData, item).body for item in result.data]

    def get_batch(self, name: str) -> Batch:
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get a single Batch for %s with name: %s', self.eid, name)

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.name, 'batches', 'id', name),
        )

        result = BatchResponse(_context={'_library': self}, **response.json())

        return cast(ResponseData, result.data).body

    def create_batch(self, asset_name: str, batch_fields: dict[str, Any]) -> Batch:
        api = SignalsNotebookApi.get_default_api()
        fields = []
        log.debug('Create Batch for %s with asset name: %s', self.eid, asset_name, extra={'batch_fields': batch_fields})

        for field in self.batch_config.fields:
            if field.name in batch_fields:
                fields.append({'id': field.id, 'value': field.to_internal_value(batch_fields[field.name])})

        request_data = BatchRequestData(type='batch', attributes=BatchAssetAttribute(fields=fields))

        response = api.call(
            method='POST',
            path=(self._get_endpoint(), self.library_name, 'assets', asset_name, 'batches'),
            json={'data': request_data.dict()},
        )

        result = BatchResponse(_context={'_library': self}, **response.json())

        return cast(ResponseData, result.data).body

    def create_asset_with_batches(
        self, asset_with_batch_fields: dict[Literal[MaterialType.ASSET, MaterialType.BATCH], dict[str, Any]]
    ) -> Asset:
        api = SignalsNotebookApi.get_default_api()
        log.debug('Create Asset with existing Batches for %s', self.eid)

        request_fields = {}

        for material_instance in asset_with_batch_fields:
            request_instance_fields = []
            config: Union[AssetConfig, BatchConfig] = self.asset_config
            if material_instance == MaterialType.BATCH:
                config = self.batch_config
            for field in config.fields:
                if field.name in asset_with_batch_fields[material_instance]:
                    request_instance_fields.append(
                        {
                            'id': field.id,
                            'value': field.to_internal_value(asset_with_batch_fields[material_instance][field.name]),
                        }
                    )

            request_fields[material_instance] = request_instance_fields

        request_data = AssetRequestData(
            type=MaterialType.ASSET,
            attributes=BatchAssetAttribute(fields=request_fields[MaterialType.ASSET]),
            relationships=AssetRelationship(
                batch=DataRelationship(
                    data=BatchRequestData(
                        type=MaterialType.BATCH,
                        attributes=BatchAssetAttribute(fields=request_fields[MaterialType.BATCH]),
                    )
                )
            ),
        )

        response = api.call(
            method='POST', path=(self._get_endpoint(), self.library_name, 'assets'), json={'data': request_data.dict()}
        )

        result = AssetResponse(_context={'_library': self}, **response.json())

        return cast(ResponseData, result.data).body
