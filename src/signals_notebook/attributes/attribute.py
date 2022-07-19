import logging
from enum import Enum
from typing import cast, Generator, Optional, Union, Any

from pydantic import BaseModel
from pydantic.fields import PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import AttrID, ObjectType, Response, ResponseData

log = logging.getLogger(__name__)


class Actions(str, Enum):
    UPDATE: str = 'update'
    DELETE: str = 'delete'
    CREATE: str = 'create'


class AttributeOption(BaseModel):
    id: Optional[str]
    key: str
    value: str
    _is_deleted: bool = PrivateAttr(default=False)
    _is_changed: bool = PrivateAttr(default=False)
    _is_created: bool = PrivateAttr(default=False)

    @property
    def is_changed(self) -> bool:
        _ = self.is_created
        return self._is_changed

    def set_value(self, new_value: str) -> None:
        self.value = new_value
        self._is_created = False
        self._is_changed = True

    @property
    def is_deleted(self) -> bool:
        _ = self.is_created
        return self._is_deleted

    def delete(self) -> None:
        self._is_created = False
        self._is_deleted = True

    def switch_created(self) -> None:
        self._is_created = not self._is_created

    @property
    def is_created(self) -> bool:
        if self._is_created:
            self._is_deleted = False
            self._is_changed = False
        return self._is_created

    @property
    def representation(self) -> Optional[dict[str, Any]]:
        if self.is_deleted:
            return {'id': self.id, 'type': ObjectType.ATTRIBUTE_OPTION, 'attributes': {'action': Actions.DELETE}}
        if self.is_created:
            return {
                'type': ObjectType.ATTRIBUTE_OPTION,
                'attributes': {
                    'action': Actions.CREATE,
                    'value': self.value,
                },
            }
        if self.is_changed:
            return {
                'id': self.id,
                'type': ObjectType.ATTRIBUTE_OPTION,
                'attributes': {
                    'action': Actions.UPDATE,
                    'value': self.value,
                },
            }
        return None


class AttributeOptionResponse(Response[AttributeOption]):
    pass


class Attribute(BaseModel):
    type: str
    id: AttrID
    name: str
    _options: list[AttributeOption] = PrivateAttr(default=[])
    _options_by_id: dict[str, AttributeOption] = PrivateAttr(default={})

    def __getitem__(self, index: Union[int, str]) -> AttributeOption:
        if not self._options:
            self._reload_options()

        if isinstance(index, int):
            return self._options[index]

        if isinstance(index, str):
            return self._options_by_id[index]

        raise IndexError('Invalid index')

    def __iter__(self):
        if not self._options:
            self._reload_options()
        return self._options.__iter__()

    def __len__(self):
        return len(self._options)

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'attributes'

    @classmethod
    def get(cls, id: AttrID) -> 'Attribute':
        """Get Attribute object by id

        Args:
            id: AttrID

        Returns:
            Attribute
        """
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), id),
        )

        result = AttributeResponse(**response.json())
        log.debug('Get Attribute with ID: %s', id)

        return cast(ResponseData, result.data).body

    @classmethod
    def get_list(cls) -> Generator['Attribute', None, None]:
        """Get all Attributes.

        Returns:
           list of available Attributes
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get List of Attributes')

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(),),
        )
        result = AttributeResponse(**response.json())

        yield from [cast(ResponseData, item).body for item in result.data]

        while result.links and result.links.next:
            response = api.call(
                method='GET',
                path=result.links.next,
            )

            result = AttributeResponse(**response.json())
            yield from [cast(ResponseData, item).body for item in result.data]

        log.debug('List of Attributes was got successfully.')

    @classmethod
    def create(
        cls,
        name: str,
        type: str,
        description: str,
        options: Optional[list[AttributeOption]] = None,
    ) -> 'Attribute':
        """Create new Attribute

        Args:
            name: name of new Attribute
            type: type of new Attribute
            description: description of new Attribute
            options: list of available options for created Attribute

        Returns:
            Attribute
        """
        api = SignalsNotebookApi.get_default_api()

        log.debug('Create Attribute: %s...', cls.__name__)

        response = api.call(
            method='POST',
            path=(cls._get_endpoint(),),
            json={
                'data': {
                    'type': ObjectType.ATTRIBUTE,
                    'attributes': {
                        'name': name,
                        'type': type,
                        'description': description,
                        'options': [option.id for option in options] if options else [],
                    },
                }
            },
        )
        log.debug('Attribute: %s was created.', cls.__name__)

        result = AttributeResponse(**response.json())
        return cast(ResponseData, result.data).body

    def append(self, option: AttributeOption) -> None:
        assert option.key
        option.switch_created()
        self._options.append(option)
        self._options_by_id[option.key] = option
        self.save()
        option.switch_created()

    def save(self) -> None:
        """Update content of Attribute by id.

        Returns:

        """
        options = []
        for option in self._options:
            if option.representation:
                options.append(option.representation)

        if not options:
            log.debug('Attribute: %s was saved successfully', self.id)
            return

        api = SignalsNotebookApi.get_default_api()
        api.call(
            method='PATCH',
            path=(self._get_endpoint(), self.id, 'options'),
            json={'data': options},
        )
        self._reload_options()
        log.debug('Attribute: %s was saved successfully', self.id)

    def delete(self) -> None:
        """Delete an Attribute by id.

        Returns:

        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Delete Attribute: %s...', self.id)

        api.call(
            method='DELETE',
            path=(self._get_endpoint(), self.id),
        )
        log.debug('Attribute: %s was deleted successfully', self.id)

    def _reload_options(self):
        self._options = []
        self._options_by_id = {}
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.id, 'options'),
        )

        result = AttributeOptionResponse(**response.json())

        for item in result.data:
            body = cast(ResponseData, item).body
            option = cast(AttributeOption, body)
            assert item.eid
            if not option.id:
                option.id = item.eid

            self._options.append(option)
            self._options_by_id[option.id] = option

    @property
    def options(self) -> list[AttributeOption]:
        """Get Attribute options

        Returns:
            list[AttributeOption]
        """
        if not self._options:
            self._reload_options()
        return self._options


class AttributeResponse(Response[Attribute]):
    pass
