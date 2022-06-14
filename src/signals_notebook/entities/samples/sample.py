import json
from typing import cast, ClassVar, Dict, Generator, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, PrivateAttr, validator

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import (
    Ancestors,
    EntityCreationRequestPayload,
    EntityType,
    Response,
    ResponseData,
)
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.samples.cell import CellPropertyContent, FieldData


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

    @property
    def is_changed(self) -> bool:
        return False if self.content is None else self.content.is_changed

    @property
    def representation_for_update(self) -> SamplePropertyBody:
        return SamplePropertyBody(id=self.id, attributes=Content(content=self.content))


class _SampleAttributes(BaseModel):
    fields: Optional[List[SampleProperty]] = []


class _SampleRelationships(BaseModel):
    template: Optional[Dict] = None
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
    fields: Optional[Dict[str, FieldData]]
    _template_name: ClassVar = 'sample.html'
    _properties: List[SampleProperty] = PrivateAttr(default=[])

    @validator('fields', pre=True)
    def set_fields(cls, values) -> Dict[str, FieldData]:
        fields: Dict[str, FieldData] = {}
        for key, value in values.items():
            fields[key] = FieldData(**value)
        return fields

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.SAMPLE

    @classmethod
    def _get_samples_endpoint(cls) -> str:
        return 'samples'

    @property
    def properties(self) -> List[SampleProperty]:
        if not self._properties:
            self._reload_properties()
        return self._properties

    def get_properties(self, property_name: Optional[str] = None) -> Generator[SampleProperty, None, None]:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_samples_endpoint(), self.eid, 'properties'),
            params={
                'name': property_name,
                'value': 'normalized',
            },
        )

        result = SamplePropertiesResponse(**response.json())
        yield from [cast(ResponseData, item).body for item in result.data]

    def _reload_properties(self) -> None:
        self._properties = []
        for item in self.get_properties():
            self._properties.append(item)

    def get_property_by_id(self, property_id: Union[str, UUID]) -> SampleProperty:
        _property_id = property_id.hex if isinstance(property_id, UUID) else property_id

        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_samples_endpoint(), self.eid, 'properties', _property_id),
            params={
                'value': 'normalized',
            },
        )

        result = SamplePropertiesResponse(**response.json())
        return cast(ResponseData, result.data).body

    def save(self, force: bool = True) -> None:
        api = SignalsNotebookApi.get_default_api()

        request_body = []
        for item in self.properties:
            if item.is_changed:
                request_body.append(item.representation_for_update.dict(exclude_none=True))

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
        fields: Optional[List[SampleProperty]] = None,
        template: Optional['Sample'] = None,
        ancestors: Optional[List[Union[Container]]] = None,  # ADD 'SamplesContainer' (warning!!! circle import)
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
                attributes=_SampleAttributes(fields=fields),
                relationships=relationships,
            )
        )

        return super()._create(
            digest=digest,
            force=force,
            request=request,
        )
