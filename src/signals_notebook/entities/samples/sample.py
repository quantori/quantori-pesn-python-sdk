import json
from typing import Literal, ClassVar, Union, Optional, cast, List, Generator
from uuid import UUID

from pydantic import Field, BaseModel, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EntityType, File, Response, ResponseData, DataList
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.entities.samples.cell import CellPropertyContent
from signals_notebook.jinja_env import env


class SampleProperty(BaseModel):
    id: Optional[Union[UUID, str]]
    name: Optional[str]
    content: Optional[CellPropertyContent]


class SamplePropertiesResponse(Response[SampleProperty]):
    pass


class Sample(ContentfulEntity):
    type: Literal[EntityType.SAMPLE] = Field(allow_mutation=False)
    _template_name: ClassVar = 'sample.html'
    _properties: List[SampleProperty] = PrivateAttr(default=[])

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.SAMPLE

    @classmethod
    def _get_samples_endpoint(cls) -> str:
        return 'samples'

    @property
    def properties(self):
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

    def patch_properties(self, property_name: Optional[str] = None, digest: str = None, force: bool = True) -> None:
        api = SignalsNotebookApi.get_default_api()

        request_body = self._get_request_body(property_name)

        response = api.call(
            method='PATCH',
            path=(self._get_samples_endpoint(), self.eid, 'properties'),
            params={
                'name': property_name,
                'digest': digest,
                'force': json.dumps(force),
                'value': 'normalized',
            },
            json={
                'data': request_body,
            },
        )
        print(response.json())
        # self._reload_properties()

    def _get_request_body(self, name):
        if name:
            return {"attributes": {"content": {"value": "test edit"}}}

        attributes = []
        for field in self.__fields__.values():
            if field.field_info.allow_mutation:
                attributes.append(
                    {
                        'id': '879cd6c6-3aaa-4060-ac8d-7f888a39d214',
                        'type': 'property',
                        'attributes': {'content': {'value': 'test edit'}},
                    },
                )

        request_body = {'attributes': {'data': attributes}}
        return request_body

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

    def patch_property_by_id(self, property_id: Union[str, UUID], digest: str = None, force: bool = True):
        _property_id = property_id.hex if isinstance(property_id, UUID) else property_id

        api = SignalsNotebookApi.get_default_api()

        request_body = {"attributes": {"content": {"value": "test edit"}}}

        response = api.call(
            method='PATCH',
            path=(self._get_samples_endpoint(), self.eid, 'properties', _property_id),
            params={
                'digest': digest,
                'force': json.dumps(force),
                'value': 'normalized',
            },
            json={
                'data': request_body,
            },
        )
        print(response.json())
        # self._reload_properties()

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
