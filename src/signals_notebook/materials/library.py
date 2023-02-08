import cgi
import io
import json
import logging
import time
import zipfile
from datetime import datetime
from enum import Enum
from typing import Any, cast, List, Literal, Optional, Union

import requests
from pydantic import BaseModel, Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import File, Links, MaterialType, MID, Response, ResponseData
from signals_notebook.materials.asset import Asset
from signals_notebook.materials.base_entity import BaseMaterialEntity
from signals_notebook.materials.batch import Batch
from signals_notebook.materials.field import AssetConfig, BatchConfig
from signals_notebook.utils.fs_handler import FSHandler

MAX_MATERIAL_FILE_SIZE = 52428800
EXPORT_ERROR_LIBRARY_EMPTY = 'Nothing to export.'

log = logging.getLogger(__name__)


class MaterialImportRule(str, Enum):
    NO_DUPLICATED = 'NO_DUPLICATED'
    TREAT_AS_UNIQUE = 'TREAT_AS_UNIQUE'
    USE_MATCHES = 'USE_MATCHES'


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
        """Get Asset config

        Returns:
            AssetConfig
        """
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
        """Set new AssetConfig

        Args:
            config: AssetConfig object

        Returns:

        """
        self._asset_config = config

    @property
    def batch_config(self) -> BatchConfig:
        """Get Batch config

        Returns:
            BatchConfig
        """
        if self._batch_config:
            return self._batch_config

        self._load_configs()
        log.debug('Checking Batch Config for %s...', self.eid)
        if self._batch_config is None:
            log.warning('Batch Config for %s cannot be None', self.eid)
        assert self._batch_config is not None, f'Batch Config for {self.eid} cannot be None'
        return self._batch_config

    @batch_config.setter
    def batch_config(self, config: BatchConfig) -> None:
        """Set Batch config

        Args:
            config: BatchConfig object

        Returns:

        """
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
        """Get list of libraries

        Returns:
            list of Library objects
        """
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
        """Fetch asset from a material library by asset ID.

        Args:
            name: asset id

        Returns:
            Asset
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get Asset for %s with name: %s', self.eid, name)

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.name, 'assets', 'id', name),
        )

        result = AssetResponse(_context={'_library': self}, **response.json())

        return cast(ResponseData, result.data).body

    def get_asset_batches(self, name: str) -> List[Batch]:
        """Fetch batches of a specified Asset.

        Args:
            name: asset id

        Returns:
            list of Batch objects
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get Asset of Batches for %s with name: %s', self.eid, name)

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.name, 'assets', name, 'batches'),
        )

        result = BatchResponse(_context={'_library': self}, **response.json())

        return [cast(ResponseData, item).body for item in result.data]

    def get_batch(self, name: str) -> Batch:
        """Fetch batch from a material library by batch ID.

        Args:
            name: batch id

        Returns:
            Batch
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get a single Batch for %s with name: %s', self.eid, name)

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.name, 'batches', 'id', name),
        )

        result = BatchResponse(_context={'_library': self}, **response.json())

        return cast(ResponseData, result.data).body

    def create_batch(self, asset_name: str, batch_fields: dict[str, Any]) -> Batch:
        """reate a new batch for designated asset.

        Args:
            asset_name: asset id
            batch_fields: fields of batch

        Returns:

        """
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

    def _process_asset_with_batch_fields(
        self, asset_with_batch_fields: dict[Literal[MaterialType.ASSET, MaterialType.BATCH], dict[str, Any]]
    ) -> AssetRequestData:
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

        return AssetRequestData(
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

    def create_asset_with_batches(
        self, asset_with_batch_fields: dict[Literal[MaterialType.ASSET, MaterialType.BATCH], dict[str, Any]]
    ) -> Asset:
        """Create new asset with batches

        Args:
            asset_with_batch_fields: dictionary of asset and batch fields

        Returns:
            Asset
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Create Asset with existing Batches for %s', self.eid)

        request_data = self._process_asset_with_batch_fields(asset_with_batch_fields)

        response = api.call(
            method='POST', path=(self._get_endpoint(), self.library_name, 'assets'), json={'data': request_data.dict()}
        )

        result = AssetResponse(_context={'_library': self}, **response.json())

        return cast(ResponseData, result.data).body

    def _is_file_ready(self, report_id: str) -> dict[str, Any]:
        api = SignalsNotebookApi.get_default_api()
        log.debug('Check job status for: %s| %s', self.__class__.__name__, self.eid)

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), 'bulkExport', 'reports', report_id),
        )
        response_attributes = response.json().get('data').get('attributes')
        status = response_attributes.get('status')
        error = response_attributes.get('error', None)

        result = {
            'success': response.status_code == 200 and status == 'COMPLETED',
            'error': error.get('description') if error else None,
        }

        return result

    def _download_file(self, file_id: str) -> requests.Response:
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get file content for: %s| %s', self.__class__.__name__, self.eid)

        return api.call(
            method='GET',
            path=(self._get_endpoint(), 'bulkExport', 'download', file_id),
        )

    def get_content(self, timeout: int = 30, period: int = 5) -> File:
        """Get library content.
        Compounds/Reagents (SNB) will be exported to SD file, others will be exported to CSV file.

        Args:
            timeout: max available time(seconds) to get file
            period: each n seconds(default value=5) api call

        Returns:
            File
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get content for: %s| %s', self.__class__.__name__, self.eid)

        bulk_export_response = api.call(
            method='POST',
            path=(self._get_endpoint(), self.name, 'bulkExport'),
        )

        file_id, report_id = bulk_export_response.json()['data']['attributes'].values()

        initial_time = time.time()

        response = None

        while time.time() - initial_time < timeout:
            result = self._is_file_ready(report_id)
            if result['error'] == EXPORT_ERROR_LIBRARY_EMPTY:
                raise FileNotFoundError('Library is empty')
            if result['success'] and not result['error']:
                response = self._download_file(file_id)
                break
            else:
                time.sleep(period)

        if not response:
            raise TimeoutError('Time is over to get file')

        content_disposition = response.headers.get('content-disposition', '')
        _, params = cgi.parse_header(content_disposition)

        return File(
            name=params['filename'], content=response.content, content_type=response.headers.get('content-type')
        )

    def _get_import_job_completed_response(self, job_id: str) -> requests.Response:
        api = SignalsNotebookApi.get_default_api()
        log.debug('Check job status for: %s| %s', self.__class__.__name__, self.eid)

        return api.call(method='GET', path=(self._get_endpoint(), 'bulkImport', 'jobs', job_id))

    def _import_materials(
        self,
        materials: Union[File, list[dict[Literal[MaterialType.ASSET, MaterialType.BATCH], dict[str, Any]]]],
        rule: MaterialImportRule = MaterialImportRule.TREAT_AS_UNIQUE,
        import_type: Literal['json', 'zip'] = 'json',
    ) -> requests.Response:

        api = SignalsNotebookApi.get_default_api()

        if isinstance(materials, File):
            if materials.size > MAX_MATERIAL_FILE_SIZE:
                raise ValueError('Available file size is 50Mb')

            return api.call(
                method='POST',
                path=(self._get_endpoint(), self.name, 'bulkImport'),
                params={
                    'rule': rule,
                    'importType': import_type,
                },
                headers={
                    'Content-Type': 'application/octet-stream',
                },
                data=materials.content,
            )

        request_body = [{'data': self._process_asset_with_batch_fields(material).dict()} for material in materials]

        return api.call(
            method='POST',
            path=(self._get_endpoint(), self.name, 'bulkImport'),
            params={
                'rule': rule,
                'importType': import_type,
            },
            json=request_body,
        )

    def bulk_import(  # type: ignore
        self,
        materials: Union[File, list[dict[Literal[MaterialType.ASSET, MaterialType.BATCH], dict[str, Any]]]],
        rule: MaterialImportRule = MaterialImportRule.TREAT_AS_UNIQUE,
        import_type: Literal['json', 'zip'] = 'json',
        timeout: int = 30,
        period: int = 5,
    ) -> Optional[File]:
        """Bulk import materials into a specified material library. Support import data from json or zip file.
        Zip file should contain the sdf file or csv file and attachments. T
        he column name in each records of sdf/csv file should be match the asset field name.
        In sdf file, it doesn't support character '-', '.', '<', '>', '=', '%', ' ',
        please replace them to '_' in records.
        Max materials size: 50MB.

        Rules of import:
        'TREAT_AS_UNIQUE', each item will be treated as a new asset. Selected by default.
        'USE_MATCHES', server will check the item with uniqueness check, if same will import as a batch.
        'NO_DUPLICATED', server will check the item with uniqueness check, duplicates are skipped and not imported.

        Args:
            materials: materials in zip or json format
            rule: rule of import
            import_type: import type: json or zip
            timeout: max available time(seconds) to get file
            period: each n seconds(default value=5) api call

        Returns:
            File or None
        """
        api = SignalsNotebookApi.get_default_api()

        bulk_import_response = self._import_materials(materials, rule, import_type)

        job_id = bulk_import_response.json()['data']['id']

        initial_time = time.time()

        response = False
        import_job_status = 'FAILED'

        while time.time() - initial_time < timeout:
            completed_import_response = self._get_import_job_completed_response(job_id)
            import_job_status = completed_import_response.json()['data']['attributes']['status']
            import_response_code = completed_import_response.status_code

            if import_response_code != 200 and import_job_status != 'COMPLETED':
                time.sleep(period)
            else:
                response = True
                log.debug('Library import is completed')
                break

        if not response and import_job_status == 'FAILED':
            log.debug('Time is over to import file')

            failure_report_reponse = api.call(
                method='GET',
                path=(self._get_endpoint(), 'bulkImport', 'jobs', job_id, 'failures'),
                params={
                    'filename': f'{self.name}_failure_report',
                },
            )
            content_disposition = failure_report_reponse.headers.get('content-disposition', '')
            _, params = cgi.parse_header(content_disposition)

            return File(
                name=params['filename'],
                content=failure_report_reponse.content,
                content_type=failure_report_reponse.headers.get('content-type'),
            )

    def dump(self, base_path: str, fs_handler: FSHandler, alias: Optional[List[str]] = None):
        metadata = {
            **{k: v for k, v in self.dict().items() if k in ('library_name', 'asset_type_id', 'eid', 'name')},
        }
        try:
            content = self.get_content(timeout=60)
            metadata['file_name'] = content.name
            file_name = content.name
            data = content.content
            fs_handler.write(
                fs_handler.join_path(base_path, self.eid, file_name),
                data,
                base_alias=alias + [metadata['name'], file_name] if alias else None,
            )
        except FileNotFoundError:
            metadata['error'] = 'Library is empty'
        except TimeoutError:
            metadata['error'] = 'Time is over to dump library'

        fs_handler.write(
            fs_handler.join_path(base_path, self.eid, 'metadata.json'),
            json.dumps(metadata),
            base_alias=alias + [metadata['name'], '__Metadata'] if alias else None,
        )

    @staticmethod
    def _generate_zip(my_file):
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_file:
            zip_file.writestr(f'summary.{my_file.content_type}', my_file.content)

        return zip_buffer

    def load(self, path: str, fs_handler: FSHandler):
        metadata_path = fs_handler.join_path(path, 'metadata.json')
        metadata = json.loads(fs_handler.read(metadata_path))

        content_path = fs_handler.join_path(path, metadata['file_name'])
        content_type = metadata['file_name'].split('.')[-1]
        content = fs_handler.read(content_path)

        materials = File(content=content, name='test', content_type=content_type)

        zip_buffer = self._generate_zip(materials)

        self.bulk_import(
            File(name='test', content=zip_buffer.getvalue(), content_type='zip'), import_type='zip', timeout=120
        )
