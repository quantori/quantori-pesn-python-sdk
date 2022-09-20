import json
import logging
from datetime import datetime
from typing import Any, cast, ClassVar, Dict, Generator, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field, PrivateAttr
from pydantic.generics import GenericModel

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import (
    EID,
    EntityClass,
    EntityCreationRequestPayload,
    EntityShortDescription,
    EntityType,
    Response,
    ResponseData,
)
from signals_notebook.jinja_env import env
from signals_notebook.utils import FSHandler

ChildClass = TypeVar('ChildClass', bound='Entity')
CellValueType = TypeVar('CellValueType')

log = logging.getLogger(__name__)
MAIN_PROPERTIES = ['Name', 'Description', 'createdAt', 'editedAt']


class Property(GenericModel, Generic[CellValueType]):
    id: Optional[Union[UUID, str]]
    type: Optional[str]
    name: Optional[str]
    description: Optional[str]
    value: Optional[CellValueType]
    values: Optional[List[CellValueType]]
    _changed: bool = PrivateAttr(default=False)

    def set_value(self, new_value: CellValueType) -> None:
        """Set new value

        Args:
            new_value: new value of Property value field

        Returns:

        """
        self.value = new_value
        self._changed = True

    @property
    def is_changed(self) -> bool:
        """Checking if content of Cell has been modified

        Returns:
            bool
        """
        return self._changed

    @property
    def representation_for_update(self) -> dict[str, dict]:
        """Get representation of body for update

        Returns:
            dict[str, dict]
        """
        return {'attributes': self.dict(include={'name', 'value'})}


class PropertiesResponse(Response[Property]):
    pass


class Entity(BaseModel):
    type: str = Field(allow_mutation=False)
    eid: EID = Field(allow_mutation=False)
    digest: Optional[str] = Field(allow_mutation=False, default=None)
    name: str = Field(title='Name')
    description: Optional[str] = Field(title='Description', default=None)
    created_at: datetime = Field(alias='createdAt', allow_mutation=False)
    edited_at: datetime = Field(alias='editedAt', allow_mutation=False)
    _template_name: ClassVar = 'entity.html'
    _properties: List[Property] = PrivateAttr(default=[])
    _properties_by_id: Dict[Union[str, UUID], Property] = PrivateAttr(default={})

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True

    def __str__(self) -> str:
        return f'<{self.__class__.__name__} eid={self.eid}>'

    def __getitem__(self, index: Union[int, str, UUID, EID]) -> Any:
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
        if not self._properties:
            self._reload_properties()
        return self._properties.__iter__()

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        raise NotImplementedError

    @classmethod
    def get_subclasses(cls) -> Generator[Type['Entity'], None, None]:
        """Get all Entity subclasses

        Returns:
            One of the Entity subclasses
        """
        log.debug('Get subclasses for: %s', cls.__name__)
        for subclass in cls.__subclasses__():
            yield from subclass.get_subclasses()
            yield subclass

    @classmethod
    def set_template_name(cls, template_name: str) -> None:
        """Set name of the template

        Args:
            template_name: template name

        Returns:

        """
        log.debug('Setting new template for: %s...', cls.__name__)
        cls._template_name = template_name
        log.debug('New template (%s) for %s was set', template_name, cls.__name__)

    @classmethod
    def get_template_name(cls) -> str:
        """Get Entity template name

        Returns:
            Template name
        """
        return cls._template_name

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'entities'

    @classmethod
    def _get_list_params(cls) -> Dict[str, Any]:
        return {
            'include_types': [cls._get_entity_type()],
        }

    def _reload_properties(self) -> None:
        log.debug('Reloading properties in Entity: %s...', self.eid)
        self._properties = []
        self._properties_by_id = {}

        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.eid, 'properties'),
        )
        result = PropertiesResponse(**response.json())
        properties = [cast(ResponseData, item).body for item in result.data]

        for item in properties:
            entity_property = cast(Property, item)
            if entity_property.name in MAIN_PROPERTIES:
                continue
            assert entity_property.id

            self._properties.append(entity_property)
            self._properties_by_id[entity_property.id] = entity_property
        log.debug('Properties in Entity: %s were reloaded', self.eid)

    @classmethod
    def get_list(cls) -> Generator['Entity', None, None]:
        """Get all entities

        Returns:
            list of entities
        """
        from signals_notebook.entities.entity_store import EntityStore

        return EntityStore.get_list(**cls._get_list_params())

    def delete(self) -> None:
        """Delete entity

        Returns:

        """
        from signals_notebook.entities.entity_store import EntityStore

        EntityStore.delete(self.eid)
        log.debug('Entity: %s was deleted from EntityStore', self.eid)

    @classmethod
    def _create(cls, *, digest: str = None, force: bool = True, request: EntityCreationRequestPayload) -> EntityClass:
        api = SignalsNotebookApi.get_default_api()
        log.debug('Create Entity: %s...', cls.__name__)

        response = api.call(
            method='POST',
            path=(cls._get_endpoint(),),
            params={
                'digest': digest,
                'force': json.dumps(force),
            },
            json=request.dict(exclude_none=True, by_alias=True),
        )
        log.debug('Entity: %s was created.', cls.__name__)

        result = Response[cls](**response.json())  # type: ignore

        return cast(ResponseData, result.data).body

    def refresh(self) -> None:
        """Refresh entity with new changes values

        Returns:

        """
        from signals_notebook.entities import EntityStore

        EntityStore.refresh(self)

    def _patch_properties(self, request_body, force: bool) -> None:
        api = SignalsNotebookApi.get_default_api()
        api.call(
            method='PATCH',
            path=(self._get_endpoint(), self.eid, 'properties'),
            params={
                'digest': None if force else self.digest,
                'force': json.dumps(force),
            },
            json={
                'data': request_body,
            },
        )

    def save(self, force: bool = True) -> None:
        """Update attributes and properties of a specified entity.

        Args:
            force: Force to update attributes and properties without doing digest check.

        Returns:

        """
        log.debug('Save Entity: %s...', self.eid)

        request_body = []
        for field in self.__fields__.values():
            if field.field_info.allow_mutation:
                request_body.append(
                    {'attributes': {'name': field.field_info.title, 'value': getattr(self, field.name)}}
                )

        log.debug('Updating properties in Entity: %s...', self.eid)
        if self._properties:
            for item in self._properties:
                if item.is_changed:
                    request_body.append(item.representation_for_update)
        self._patch_properties(request_body=request_body, force=force)
        self._reload_properties()

        log.debug('Properties in Entity: %s were updated successfully', self.eid)
        log.debug('Entity: %s was saved.', self.eid)

    @property
    def short_description(self) -> EntityShortDescription:
        """Return EntityShortDescription of Entity

        Returns:
            EntityShortDescription
        """
        return EntityShortDescription(type=self.type, id=self.eid)

    def get_html(self) -> str:
        """Get in HTML format

        Returns:
            Rendered HTML in string format
        """
        data = {'name': self.name, 'edited_at': self.edited_at, 'type': self.type, 'description': self.description}
        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(data=data)

    def dump(self, base_path: str, fs_handler: FSHandler, alias: Optional[List[str]] = None) -> None:
        log.error('Dumping is not implemented')

    @classmethod
    def _load(cls, path: str, fs_handler: FSHandler, parent: Any) -> None:
        log.error('Loading is not implemented')

    @classmethod
    def dump_templates(cls, base_path: str, fs_handler: FSHandler) -> None:
        """Dump Entity templates

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
                fs_handler.write(
                    fs_handler.join_path(base_path, 'templates', entity_type, f'metadata_{template.name}.json'),
                    json.dumps({k: v for k, v in template.dict().items() if k in ('name', 'description', 'eid')}),
                    base_alias=['Templates', entity_type, template.name],
                )

        except TypeError:
            pass
