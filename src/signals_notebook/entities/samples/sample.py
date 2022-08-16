import json
import logging
from typing import cast, Dict, List, Literal, Optional, TYPE_CHECKING, Union, Tuple
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

        if isinstance(index, UUID):
            return self._cells_by_id[index]

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
        cells = [cast(ResponseData, item).body for item in result.data]

        for item in cells:
            sample_cell = cast(SampleCell, item)
            assert sample_cell.id

            self._cells.append(sample_cell)
            self._cells_by_id[sample_cell.id] = sample_cell
        log.debug('Cells for Sample: %s were reloaded', self.eid)

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

        metadata = {k: v for k, v in self.dict().items() if k in ('name', 'description', 'eid')}
        fs_handler.write(fs_handler.join_path(base_path, self.eid, 'metadata.json'), json.dumps(metadata))
        data = [item.dict() for item in self]
        fs_handler.write(
            fs_handler.join_path(base_path, self.eid, f'{self.name}.json'),
            json.dumps({'data': data}, default=str).encode('utf-8'),
        )

    @classmethod
    def dump_templates(cls, base_path: str, fs_handler: FSHandler, base_alias: Tuple[str]) -> None:
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
                template.dump(fs_handler.join_path(base_path, 'templates', entity_type), fs_handler,
                              ('Templates', entity_type, template.name))

        except TypeError:
            pass
