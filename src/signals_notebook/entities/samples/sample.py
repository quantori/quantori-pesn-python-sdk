import json
import logging
from typing import cast, Dict, List, Literal, Optional, TYPE_CHECKING, Union
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
from signals_notebook.entities.samples.cell import SampleCell
from signals_notebook.utils import FSHandler

if TYPE_CHECKING:
    from signals_notebook.entities import SamplesContainer

log = logging.getLogger(__name__)


class _SampleAttributes(BaseModel):
    fields: Optional[List[SampleCell]] = []


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
                return self._cells_by_id[UUID(index)]
            except ValueError:
                return self._cells_by_id[index]

        # if isinstance(index, UUID):
        #     return self._cells_by_id[index]

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
            sample_cell.read_only = item.meta.get('definition').get('readOnly', False)
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
        cells: Optional[List[SampleCell]] = None,
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

    def dump(self, base_path: str, fs_handler: FSHandler) -> None:
        """Dump Sample entity

        Args:
            base_path: content path where create dump
            fs_handler: FSHandler

        Returns:

        """

        metadata = {
            'filename': f'{self.name}.json',
            'columns': self.get_column_definitions_list(),
            **{k: v for k, v in self.dict().items() if k in ('name', 'description', 'eid')},
        }
        fs_handler.write(fs_handler.join_path(base_path, self.eid, 'metadata.json'), json.dumps(metadata))
        data = [item.dict() for item in self]
        fs_handler.write(
            fs_handler.join_path(base_path, self.eid, f'{self.name}.json'),
            json.dumps({'data': data}, default=str).encode('utf-8'),
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
        from signals_notebook.entities import EntityStore

        log.debug('Loading sample from dump...')

        entity_type = cls._get_entity_type()
        # metadata_path = fs_handler.join_path(path, 'metadata.json')
        # metadata = json.loads(fs_handler.read(metadata_path))
        # content_path = fs_handler.join_path(path, metadata['file_name'])
        # content_bytes = fs_handler.read(content_path)
        metadata = {
            "eid": "sample:b171650b-fba0-4d49-b438-d5478aad6b06",
            "name": "Sample-1797",
            "description": "",
            'columns': [
                'ID',
                'Template',
                None,
                None,
                'Created Date',
                'Description',
                'Comments',
                'Amount',
                # 'Chemical Name',
                # 'FM',
                # 'EM',
                # 'MF',
                # 'MW',
                'Attached Docs',
                'ID',
                'Template',
            ],
        }
        # content_bytes = b'{"data": [{"id": "b718adec-73e0-3ce3-ac72-0dd11a06a308", "name": "ID", "content": {"value": "Sample-1797", "name": null, "eid": null, "values": null}}, {"id": "278c491b-dd8a-3361-8c14-9c4ac790da34", "name": "Template", "content": {"value": "Chemical Sample", "name": null, "eid": null, "values": null}}, {"id": "digests.self", "name": null, "content": {"value": "9febec4d41fbdd23c86305401ece8693512670e7269e77f3474df8b2ee6f8696", "name": null, "eid": null, "values": null}}, {"id": "digests.external", "name": null, "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "1", "name": "Created Date", "content": {"value": "2022-08-04T10:15:08.296900609Z", "name": null, "eid": null, "values": null}}, {"id": "2", "name": "Description", "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "3", "name": "Comments", "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "4", "name": "Amount", "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "5", "name": "Chemical Name", "content": {"value": "methyl (E)-2-(2-chloro-6-fluorobenzylidene)-5-(4-((furan-2-carbonyl)oxy)phenyl)-7-methyl-3-oxo-2,3-dihydro-5H-thiazolo[3,2-a]pyrimidine-6-carboxylate", "name": null, "eid": null, "values": null}}, {"id": "6", "name": "FM", "content": {"value": "552.96", "name": null, "eid": null, "values": null}}, {"id": "7", "name": "EM", "content": {"value": "552.05581", "name": null, "eid": null, "values": null}}, {"id": "8", "name": "MF", "content": {"value": "C27H18ClFN2O6S", "name": null, "eid": null, "values": null}}, {"id": "9", "name": "MW", "content": {"value": "552.96", "name": null, "eid": null, "values": null}}, {"id": "10", "name": "Attached Docs", "content": {"value": "0", "name": null, "eid": "sample:b171650b-fba0-4d49-b438-d5478aad6b06", "values": null}}, {"id": "sampleId", "name": "ID", "content": {"value": "sample:b171650b-fba0-4d49-b438-d5478aad6b06", "name": null, "eid": null, "values": null}}, {"id": "sourceName", "name": "Template", "content": {"value": "Chemical Sample", "name": null, "eid": null, "values": null}}]}'
        # content_bytes = b'{"data": [{"id": "b718adec-73e0-3ce3-ac72-0dd11a06a308", "name": "ID", "content": {"value": "Sample-1795", "name": null, "eid": null, "values": null}}, {"id": "278c491b-dd8a-3361-8c14-9c4ac790da34", "name": "Template", "content": {"value": "Sample", "name": null, "eid": null, "values": null}}, {"id": "digests.self", "name": null, "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "digests.external", "name": null, "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "1", "name": "Created Date", "content": {"value": "2022-08-04T10:10:10.457242220Z", "name": null, "eid": null, "values": null}}, {"id": "2", "name": "Description", "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "3", "name": "Comments", "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "4", "name": "Amount", "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "10", "name": "Attached Docs", "content": {"value": "0", "name": null, "eid": "sample:abc5a847-1eb1-4f68-b26f-b31697b08b59", "values": null}}, {"id": "sampleId", "name": "ID", "content": {"value": "sample:abc5a847-1eb1-4f68-b26f-b31697b08b59", "name": null, "eid": null, "values": null}}, {"id": "sourceName", "name": "Template", "content": {"value": "Sample", "name": null, "eid": null, "values": null}}]}'
        content_bytes = b'{"data": [{"id": "b718adec-73e0-3ce3-ac72-0dd11a06a308", "name": "ID", "content": {"value": "Sample-1832", "name": null, "eid": null, "values": null}}, {"id": "278c491b-dd8a-3361-8c14-9c4ac790da34", "name": "Template", "content": {"value": "Sample", "name": null, "eid": null, "values": null}}, {"id": "digests.self", "name": null, "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "digests.external", "name": null, "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "1", "name": "Created Date", "content": {"value": "2022-08-18T13:32:52.734439882Z", "name": null, "eid": null, "values": null}}, {"id": "2", "name": "Description", "content": {"value": "create sample", "name": null, "eid": null, "values": null}}, {"id": "3", "name": "Comments", "content": {"value": "create sample 2", "name": null, "eid": null, "values": null}}, {"id": "4", "name": "Amount", "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "10", "name": "Attached Docs", "content": {"value": "0", "name": null, "eid": "sample:234d7b0d-82f8-4ee1-a6fd-4be23c653874", "values": null}}, {"id": "sampleId", "name": "ID", "content": {"value": "sample:234d7b0d-82f8-4ee1-a6fd-4be23c653874", "name": null, "eid": null, "values": null}}, {"id": "sourceName", "name": "Template", "content": {"value": "Sample", "name": null, "eid": null, "values": null}}]}'
        # content_bytes = b'{"data": [{"id": "b718adec-73e0-3ce3-ac72-0dd11a06a308", "name": "ID", "content": {"value": "Sample-1798", "name": null, "eid": null, "values": null}}, {"id": "278c491b-dd8a-3361-8c14-9c4ac790da34", "name": "Template", "content": {"value": "Sample", "name": null, "eid": null, "values": null}}, {"id": "digests.self", "name": null, "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "digests.external", "name": null, "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "1", "name": "Created Date", "content": {"value": "2022-08-04T10:15:27.151611856Z", "name": null, "eid": null, "values": null}}, {"id": "2", "name": "Description", "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "3", "name": "Comments", "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "4", "name": "Amount", "content": {"value": "4", "name": null, "eid": null, "values": null}}, {"id": "10", "name": "Attached Docs", "content": {"value": "0", "name": null, "eid": "sample:4bcfd751-9c36-42f8-8841-3c3acc39d5a8", "values": null}}, {"id": "sampleId", "name": "ID", "content": {"value": "sample:4bcfd751-9c36-42f8-8841-3c3acc39d5a8", "name": null, "eid": null, "values": null}}, {"id": "sourceName", "name": "Template", "content": {"value": "Sample", "name": null, "eid": null, "values": null}}, {"id": "5", "name": "Chemical Name", "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "6", "name": "FM", "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "7", "name": "EM", "content": {"value": null, "name": null, "eid": null, "values": null}}, {"id": "8", "name": "MF", "content": {"value": 4, "name": null, "eid": null, "values": null}}, {"id": "9", "name": "MW", "content": {"value": null, "name": null, "eid": null, "values": null}}]}'
        content = json.loads(content_bytes)['data']
        to_delete = []
        for item in content:
            if item['name'] is None:
                to_delete.append(item)
            item.pop('name')

        for item in to_delete:
            content.remove(item)
        cells = []
        for item in content:
            try:
                int(item['id'])
                cells.append(SampleCell(**item))
                # TODO: check read-only property in meta
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
                print(template)
                print(cells)
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
                template.dump(fs_handler.join_path(base_path, 'templates', entity_type), fs_handler)
        except TypeError:
            pass
