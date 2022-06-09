import json
from typing import cast, ClassVar, Dict, Generator, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, PrivateAttr, validator

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EntityType, File, Response, ResponseData
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.entities.samples.cell import CellPropertyContent, FieldData
from signals_notebook.jinja_env import env


class SampleProperty(BaseModel):
    id: Optional[Union[UUID, str]]
    name: Optional[str]
    content: Optional[CellPropertyContent]

    @property
    def is_changed(self) -> bool:
        return self.content.is_changed  # type: ignore

    @property
    def representation_for_update(self):
        return {'id': self.id, 'type': 'property', 'attributes': {'content': self.content.dict(exclude_none=True)}}

    @property
    def representation_for_update_by_id(self):
        return {'attributes': {'content': self.content.dict(exclude_none=True)}}


class SamplePropertiesResponse(Response[SampleProperty]):
    pass


class Sample(ContentfulEntity):
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

    def save(self, property_name: Optional[str] = None, digest: str = None, force: bool = True) -> None:
        api = SignalsNotebookApi.get_default_api()

        request_body = []
        for item in self._properties:
            if item.is_changed:
                request_body.append(item.representation_for_update)

        api.call(
            method='PATCH',
            path=(self._get_samples_endpoint(), self.eid, 'properties'),
            params={
                'name': property_name,
                'digest': digest,
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
        container: Container,
        name: str,
        content_type: str,
        content: bytes = b'',
        force: bool = True,
    ) -> Entity:
        return container.add_child(
            name=name,
            content=content,
            content_type=content_type,
            force=force,
        )  # TODO: rewrite this method by Sergey's way

    def get_content(self) -> File:
        return super()._get_content()

    def get_html(self) -> str:
        file = self._get_content()
        data = {'name': self.name, 'content': file.content.decode('utf-8')}
        template = env.get_template(self._template_name)

        return template.render(data=data)
