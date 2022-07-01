import json
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

if TYPE_CHECKING:
    from signals_notebook.entities import SamplesContainer


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

    def save(self, force: bool = True) -> None:
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
