import logging
from enum import Enum
from typing import cast, Generator, Literal, Optional

from pydantic import BaseModel
from pydantic.fields import PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import AttrID, ObjectType, Response, ResponseData

log = logging.getLogger(__name__)


class Action(str, Enum):
    UPDATE = 'update'
    DELETE = 'delete'
    CREATE = 'create'


class _Attributes(BaseModel):
    action: Action
    value: Optional[str]


class _OptionRepresentation(BaseModel):
    id: Optional[str]
    type: Literal[ObjectType.ATTRIBUTE_OPTION] = ObjectType.ATTRIBUTE_OPTION
    attributes: _Attributes


class _AttributeOption(BaseModel):
    value: str


class _AttributeOptionResponse(Response[_AttributeOption]):
    pass


class Attribute(BaseModel):
    type: str
    id: AttrID
    name: str
    _options: list[str] = PrivateAttr(default=[])

    def __init__(self, *args, **kwargs):
        self._options = kwargs.pop('options', [])
        super().__init__(*args, **kwargs)
        self.type = ObjectType.CHOICE

    def __iter__(self):
        if not self._options:
            self._reload_options()
        return self._options.__iter__()

    def __len__(self) -> int:
        if not self._options:
            self._reload_options()
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
        description: str,
        options: list[str] = None,
    ) -> 'Attribute':
        """Create new Attribute

        Args:
            name: name of new Attribute
            description: description of new Attribute
            options: list of available id options for created Attribute

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
                        'type': ObjectType.CHOICE,
                        'description': description,
                        'options': options or [],
                    },
                }
            },
        )
        log.debug('Attribute: %s was created.', cls.__name__)

        result = AttributeResponse(**response.json())
        return cast(ResponseData, result.data).body

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

    def add_option(self, option: str) -> None:
        """Update option of Attribute by id.

        Args:
            option: option which will be added to option list in Attribute

        Returns:

        """
        new_option = _OptionRepresentation(attributes=_Attributes(action=Action.CREATE, value=option))
        log.debug('Creating Option: %s...', self.id)
        self._patch_options(new_option)

    def delete_option(self, option: str) -> None:
        """Delete option of Attribute by id.

        Args:
            option: option which will be deleted from Attribute's option list

        Returns:

        """
        deleted_option = _OptionRepresentation(id=option, attributes=_Attributes(action=Action.DELETE))
        log.debug('Deleting Option: %s...', self.id)
        self._patch_options(deleted_option)

    def update_option(self, old_option: str, new_option: str) -> None:
        """Update option of Attribute by id.

        Args:
            old_option: old option which will be updated
            new_option: new option value

        Returns:

        """
        option = _OptionRepresentation(id=old_option, attributes=_Attributes(action=Action.UPDATE, value=new_option))
        log.debug('Patching Option: %s...', self.id)
        self._patch_options(option)

    def _patch_options(self, option: _OptionRepresentation) -> None:
        api = SignalsNotebookApi.get_default_api()
        api.call(
            method='PATCH',
            path=(self._get_endpoint(), self.id, 'options'),
            json={'data': [option.dict(exclude_none=True)]},
        )
        self._reload_options()
        log.debug('Attribute: %s was reloaded successfully', self.id)

    def _reload_options(self):
        self._options = []
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.id, 'options'),
        )

        result = _AttributeOptionResponse(**response.json())

        for item in result.data:
            body = cast(ResponseData, item).body
            option = cast(_AttributeOption, body)

            self._options.append(option.value)

    @property
    def options(self) -> list[str]:
        """Get Attribute options

        Returns:
            list[str]
        """
        if not self._options:
            self._reload_options()
        return self._options


class AttributeResponse(Response[Attribute]):
    pass
