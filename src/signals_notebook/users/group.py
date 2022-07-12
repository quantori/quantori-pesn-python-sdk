import json
import logging
from datetime import datetime
from typing import cast, Generator, Literal

from pydantic import BaseModel, Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import ObjectType, Response, ResponseData
from signals_notebook.users.user import User


log = logging.getLogger(__name__)


class GroupMember(BaseModel):
    user_id: str = Field(alias='userId')
    user_name: str = Field(alias='userName')
    first_name: str = Field(alias='firstName')
    last_name: str = Field(alias='lastName')


class GroupMemberResponse(Response[GroupMember]):
    pass


class Group(BaseModel):
    type: Literal[ObjectType.GROUP] = Field(allow_mutation=False)
    id: str
    is_system: bool = Field(alias='isSystem', allow_mutation=False)
    name: str
    description: str
    created_at: datetime = Field(alias='createdAt', allow_mutation=False)
    edited_at: datetime = Field(alias='editedAt', allow_mutation=False)
    digest: str

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'groups'

    @classmethod
    def get_list(cls) -> Generator['Group', None, None]:
        """Get all groups

        Returns:
            Group
        """
        api = SignalsNotebookApi.get_default_api()
        response = api.call(
            method='GET',
            path=(cls._get_endpoint(),),
        )
        result = GroupResponse(**response.json())
        yield from [cast(ResponseData, item).body for item in result.data]

        while result.links and result.links.next:
            response = api.call(
                method='GET',
                path=result.links.next,
            )

            result = GroupResponse(**response.json())
            yield from [cast(ResponseData, item).body for item in result.data]

    @classmethod
    def get(cls, group_id: str) -> 'Group':
        """Get group by id

        Args:
            group_id: Unique user group identifier
        Returns:
            Group
        """
        api = SignalsNotebookApi.get_default_api()
        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), group_id),
        )
        result = GroupResponse(**response.json())
        return cast(ResponseData, result.data).body

    @classmethod
    def create(cls, is_system: bool, name: str, description: str) -> 'Group':
        """Create new Group

        Returns:
            Group
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Create User: %s...', cls.__name__)

        response = api.call(
            method='POST',
            path=(cls._get_endpoint(),),
            json={'data': {'attributes': {'name': name, 'description': description, 'isSystem': is_system}}},
        )
        log.debug('Group: %s was created.', cls.__name__)

        result = GroupResponse(**response.json())
        return cast(ResponseData, result.data).body

    def save(self, force: bool = True) -> None:
        """Update attributes of a specified group.

        Returns:

        """
        api = SignalsNotebookApi.get_default_api()
        api.call(
            method='PATCH',
            path=(
                self._get_endpoint(),
                self.id,
            ),
            params={
                'force': json.dumps(force),
            },
            json={
                'data': {
                    'attributes': self.dict(
                        include={
                            'name',
                            'description',
                        },
                    )
                },
            },
        )

    def delete(self):
        """Delete user group by id.

        Returns:

        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Disable Group: %s...', self.id)

        api.call(
            method='DELETE',
            path=(self._get_endpoint(), self.id),
        )
        log.debug('Group: %s was disabled successfully', self.id)

    def get_members(self) -> list[GroupMember]:
        """Get user group members

        Returns:
            Group members
        """
        api = SignalsNotebookApi.get_default_api()
        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.id, 'members'),
        )
        result = GroupMemberResponse(**response.json())
        return [cast(ResponseData, item).body for item in result.data]

    def add_user(self, user: User, force: bool = True) -> list[GroupMember]:
        """Add user to user group

        Args:
            user: User object
            force: Force to update

        Returns:
            list[GroupMember]
        """
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='POST',
            path=(self._get_endpoint(), self.id, 'members'),
            params={
                'force': json.dumps(force),
            },
            json={
                'data': {
                    'attributes': {'userId': user.id},
                }
            },
        )

        result = GroupMemberResponse(**response.json())
        return [cast(ResponseData, item).body for item in result.data]

    def delete_user(self, user: User) -> None:
        """Delete user from user group.

        Args:
            user: User object

        Returns:

        """
        api = SignalsNotebookApi.get_default_api()

        api.call(
            method='DELETE',
            path=(self._get_endpoint(), self.id, 'members', user.id),
        )


class GroupResponse(Response[Group]):
    pass
