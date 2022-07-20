import logging
from enum import Enum
from typing import cast, Generator, Literal, Optional, Union

from pydantic import BaseModel
from pydantic.fields import PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import AttrID, ObjectType, Response, ResponseData

log = logging.getLogger(__name__)


class Action(str, Enum):
    UPDATE: str = 'update'
    DELETE: str = 'delete'
    CREATE: str = 'create'


class _Attributes(BaseModel):
    action: Action
    value: Optional[str]


class _OptionRepresentation(BaseModel):
    id: Optional[str]
    type: Literal[ObjectType.ATTRIBUTE_OPTION] = ObjectType.ATTRIBUTE_OPTION
    attributes: _Attributes


class AttributeOption(BaseModel):
    id: Optional[str]
    key: str
    value: str


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

    def add_option(self, value: str) -> None:
        """Update option of Attribute by id.

        Args:
            value: AttributeOption value which will be added to option list in Attribute

        Returns:

        """
        option = _OptionRepresentation(attributes=_Attributes(action=Action.CREATE, value=value))
        log.debug('Creating Option: %s...', self.id)
        self._patch_options(option)

    def delete_option(self, id: str) -> None:
        """Delete option of Attribute by id.

        Args:
            id: AttributeOption id which will be deleted from Attribute's option list

        Returns:

        """
        option = _OptionRepresentation(id=str(id), attributes=_Attributes(action=Action.DELETE))
        log.debug('Deleting Option: %s...', self.id)
        self._patch_options(option)

    def update_option(self, id: str, value: str) -> None:
        """Update option of Attribute by id.

        Args:
            id: AttributeOption id
            value: AttributeOption value which will be updated

        Returns:

        """
        option = _OptionRepresentation(id=id, attributes=_Attributes(action=Action.UPDATE, value=value))
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
