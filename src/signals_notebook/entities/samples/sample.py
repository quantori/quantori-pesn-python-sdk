import json
import logging
from typing import Any, cast, Dict, List, Literal, Optional, TYPE_CHECKING, Union
from uuid import UUID

from pydantic import BaseModel, Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import (
    Ancestors,
    EntityCreationRequestPayload,
    EntityShortDescription,
    EntityType,
    Response,
    ResponseData,
)
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.samples.cell import SampleCell, SampleCellContent
from signals_notebook.utils import FSHandler

if TYPE_CHECKING:
    from signals_notebook.entities import SamplesContainer

log = logging.getLogger(__name__)


class SampleCellBody(BaseModel):
    id: Optional[str]
    content: SampleCellContent = Field(default=SampleCellContent())


class _SampleAttributes(BaseModel):
    fields: Optional[List[SampleCellBody]] = []


class _SampleRelationships(BaseModel):
    template: Optional[Dict[str, EntityShortDescription]] = None
    ancestors: Optional[Ancestors] = None


class _SampleRequestBody(BaseModel):
    type: EntityType
    attributes: _SampleAttributes
    relationships: Optional[_SampleRelationships] = None


class _SampleRequestPayload(EntityCreationRequestPayload[_SampleRequestBody]):
    pass


class SampleCellsResponse(Response[SampleCell]):
    pass


class Sample(Entity):
    type: Literal[EntityType.SAMPLE] = Field(allow_mutation=False)
    _cells: List[SampleCell] = PrivateAttr(default=[])
    _cells_by_id: Dict[Union[str, UUID], SampleCell] = PrivateAttr(default={})

    def __getitem__(self, index: Union[int, str, UUID]) -> SampleCell:
        if not self._cells:
            self._reload_cells()

        if isinstance(index, int):
            return self._cells[index]

        if isinstance(index, str):
            try:
                return self._cells_by_id[index]
            except KeyError as e:
                raise e

        raise IndexError('Invalid index')

    def __iter__(self):
        if not self._cells:
            self._reload_cells()
        return self._cells.__iter__()

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.SAMPLE

    @classmethod
    def _get_samples_endpoint(cls) -> str:
        return 'samples'

    def _reload_cells(self) -> None:
        log.debug('Reloading cells for Sample: %s...', self.eid)
        self._cells = []
        self._cells_by_id = {}

        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_samples_endpoint(), self.eid, 'properties'),
            params={'value': 'normalized'},
        )

        result = SampleCellsResponse(**response.json())
        cells = [cast(ResponseData, item) for item in result.data]

        for item in cells:
            sample_cell = cast(SampleCell, item.body)
            sample_cell.read_only = getattr(item, 'meta', {}).get('definition', {}).get('readOnly', False)
            assert sample_cell.id

            self._cells.append(sample_cell)
            self._cells_by_id[sample_cell.id] = sample_cell
        log.debug('Cells for Sample: %s were reloaded', self.eid)

    def get_column_definitions_list(self) -> List[str]:
        if not self._cells:
            self._reload_cells()
        return [item.name for item in self]

    def save(self, force: bool = True) -> None:
        """Save Sample.

        Args:
            force: Force to update content without doing digest check.

        Returns:

        """
        log.debug('Saving Sample: %s...', self.eid)
        api = SignalsNotebookApi.get_default_api()

        request_body = []
        for item in self._cells:
            if item.is_changed:
                request_body.append(item.representation_for_update.dict(exclude_none=True))

        if not request_body:
            return

        api.call(
            method='PATCH',
            path=(self._get_samples_endpoint(), self.eid, 'properties'),
            params={
                'force': json.dumps(force),
                'value': 'normalized',
            },
            json={
                'data': {'attributes': {'data': request_body}},
            },
        )
        self._reload_cells()
        log.debug('Sample: %s were saved successfully.', self.eid)

    @classmethod
    def create(
        cls,
        *,
        cells: Optional[List[SampleCellBody]] = None,
        template: Optional['Sample'] = None,
        ancestors: Optional[List[Union[Container, 'SamplesContainer']]] = None,
        digest: str = None,
        force: bool = True,
    ) -> 'Sample':
        """Create Sample Entity

        Args:
            cells: Sample's data
            template: template for Sample creation
            ancestors: Container or SamplesContainer where create new Sample
            digest: Indicate digest of entity. It is used to avoid conflict while concurrent editing.
                If the parameter 'force' is true, this parameter is optional.
                If the parameter 'force' is false, this parameter is required.
            force: Force to create without doing digest check

        Returns:
            Sample
        """
        log.debug('Create Sample: %s ', cls.__name__)

        relationships = None
        if template or ancestors:
            relationships = _SampleRelationships(
                ancestors=Ancestors(data=[item.short_description for item in ancestors]) if ancestors else None,
                template={'data': template.short_description} if template else None,
            )

        request = _SampleRequestPayload(
            data=_SampleRequestBody(
                type=cls._get_entity_type(),
                attributes=_SampleAttributes(fields=cells),
                relationships=relationships,
            )
        )

        return super()._create(
            digest=digest,
            force=force,
            request=request,
        )

    def dump(self, base_path: str, fs_handler: FSHandler, alias: Optional[List[str]] = None) -> None:
        """Dump Sample entity

        Args:
            base_path: content path where create dump
            fs_handler: FSHandler
            alias: Backup alias

        Returns:

        """

        metadata = {
            'filename': f'{self.name}.json',
            'columns': self.get_column_definitions_list(),
            **{k: v for k, v in self.dict().items() if k in ('name', 'description', 'eid')},
        }
        fs_handler.write(
            fs_handler.join_path(base_path, self.eid, 'metadata.json'),
            json.dumps(metadata),
            base_alias=alias + [self.name, '__Metadata'] if alias else None,
        )
        data = [item.dict() for item in self]
        fs_handler.write(
            fs_handler.join_path(base_path, self.eid, f'{self.name}.json'),
            json.dumps({'data': data}, default=str).encode('utf-8'),
            base_alias=alias + [self.name, f'{self.name}.json'] if alias else None,
        )

    @classmethod
    def load(cls, path: str, fs_handler: FSHandler, parent: Container) -> None:
        """Load Sample entity

        Args:
            path: content path
            fs_handler: FSHandler
            parent: Container where load Sample entity

        Returns:

        """
        cls._load(path, fs_handler, parent)

    @classmethod
    def _load(cls, path: str, fs_handler: FSHandler, parent: Any) -> None:
        from signals_notebook.entities import EntityStore

        log.debug('Loading sample from dump...')

        entity_type = cls._get_entity_type()
        metadata_path = fs_handler.join_path(path, 'metadata.json')
        metadata = json.loads(fs_handler.read(metadata_path))

        sample_filename = metadata['filename']
        sample_data_path = fs_handler.join_path(path, sample_filename)
        sample_content = json.loads(fs_handler.read(sample_data_path))['data']

        cells = []
        for item in sample_content:
            if not item['read_only'] and item['name'] != 'Amount':
                try:
                    int(item['id'])
                    cells.append(SampleCellBody(**item))
                except ValueError:
                    pass

        column_definitions = metadata.get('columns')
        templates = EntityStore.get_list(
            include_types=[entity_type], include_options=[EntityStore.IncludeOptions.TEMPLATE]
        )
        for item in templates:
            template = cast('Sample', item)
            template_column_definitions = template.get_column_definitions_list()
            if set(template_column_definitions) == set(column_definitions):
                cls.create(
                    ancestors=[parent],
                    template=template,
                    cells=cells,
                )
                break

    @classmethod
    def dump_templates(cls, base_path: str, fs_handler: FSHandler) -> None:
        """Dump Sample templates

        Args:
            base_path: content path where create templates dump
            fs_handler: FSHandler

        Returns:

        """
        from signals_notebook.entities import EntityStore

        entity_type = cls._get_entity_type()

        templates = EntityStore.get_list(
            include_types=[entity_type], include_options=[EntityStore.IncludeOptions.TEMPLATE]
        )
        try:
            for template in templates:
                template.dump(
                    fs_handler.join_path(base_path, 'templates', entity_type),
                    fs_handler,
                    ['Templates', entity_type.value],
                )

        except TypeError:
            pass
