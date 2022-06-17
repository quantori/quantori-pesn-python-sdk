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
from signals_notebook.entities.samples.cell import CellPropertyContent, CellValueType

if TYPE_CHECKING:
    from signals_notebook.entities import SamplesContainer


class Content(BaseModel):
    content: Optional[CellPropertyContent]


class SamplePropertyBody(BaseModel):
    id: Optional[Union[UUID, str]]
    type: str = 'property'
    attributes: Content


class SampleProperty(BaseModel):
    id: Optional[Union[UUID, str]]
    name: Optional[str]
    content: CellPropertyContent = Field(default=CellPropertyContent())

    def set_content_value(self, new_value: CellValueType) -> None:
        self.content.set_value(new_value)

    def set_content_values(self, new_values: List[CellValueType]) -> None:
        self.content.set_values(new_values)

    def set_content_name(self, new_name: str) -> None:
        self.content.set_name(new_name)

    @property
    def content_value(self) -> Optional[CellValueType]:
        return self.content.value

    @property
    def content_values(self) -> Optional[List[CellValueType]]:
        return self.content.values

    @property
    def content_name(self) -> Optional[str]:
        return self.content.name

    @property
    def is_changed(self) -> bool:
        return False if self.content is None else self.content.is_changed

    @property
    def representation_for_update(self) -> SamplePropertyBody:
        return SamplePropertyBody(id=str(self.id), attributes=Content(content=self.content))


class _SampleAttributes(BaseModel):
    fields: Optional[List[SampleProperty]] = []


class _SampleRelationships(BaseModel):
    template: Optional[Dict[str, EntityShortDescription]] = None
    ancestors: Optional[Ancestors] = None


class _SampleRequestBody(BaseModel):
    type: EntityType
    attributes: _SampleAttributes
    relationships: Optional[_SampleRelationships] = None


class _SampleRequestPayload(EntityCreationRequestPayload[_SampleRequestBody]):
    pass


class SamplePropertiesResponse(Response[SampleProperty]):
    pass


class Sample(Entity):
    type: Literal[EntityType.SAMPLE] = Field(allow_mutation=False)
    _properties: List[SampleProperty] = PrivateAttr(default=[])
    _properties_by_id: Dict[Union[str, UUID], SampleProperty] = PrivateAttr(default={})

    def __getitem__(self, index: Union[int, str, UUID]) -> SampleProperty:
        if not self._properties:
            self._reload_properties()

        if isinstance(index, int):
            return self._properties[index]

        if isinstance(index, str):
            try:
                return self._properties_by_id[UUID(index)]
            except ValueError:
                return self._properties_by_id[index]

        if isinstance(index, UUID):
            return self._properties_by_id[index]

        raise IndexError('Invalid index')

    def __iter__(self):
        return self._properties.__iter__()

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.SAMPLE

    @classmethod
    def _get_samples_endpoint(cls) -> str:
        return 'samples'

    def _reload_properties(self) -> None:
        self._properties = []
        self._properties_by_id = {}

        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_samples_endpoint(), self.eid, 'properties'),
            params={'value': 'normalized'},
        )

        result = SamplePropertiesResponse(**response.json())
        properties = [cast(ResponseData, item).body for item in result.data]

        for item in properties:
            sample_property = cast(SampleProperty, item)
            assert sample_property.id

            self._properties.append(sample_property)
            self._properties_by_id[sample_property.id] = sample_property

    def save(self, force: bool = True) -> None:
        api = SignalsNotebookApi.get_default_api()

        request_body = []
        for item in self._properties:
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
        self._reload_properties()

    @classmethod
    def create(
        cls,
        *,
        properties: Optional[List[SampleProperty]] = None,
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
                attributes=_SampleAttributes(fields=properties),
                relationships=relationships,
            )
        )

        return super()._create(
            digest=digest,
            force=force,
            request=request,
        )
