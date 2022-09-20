import cgi
import json
import logging
import mimetypes
from datetime import datetime
from typing import Any, cast, Generator, Optional, TYPE_CHECKING, Union

from pydantic import BaseModel, Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import File, Response, ResponseData
from signals_notebook.users.role import Role

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from signals_notebook.users.group import Group


class Licence(BaseModel):
    id: Union[int, str]
    name: str
    expires_at: datetime = Field(alias='expiresAt')
    valid: bool
    has_service_expired: bool = Field(alias='hasServiceExpired')
    has_user_found: bool = Field(alias='hasUserFound')
    has_user_activated: bool = Field(alias='hasUserActivated')

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True


class BaseUser(BaseModel):
    id: str = Field(alias='userId', allow_mutation=False)
    first_name: str = Field(alias='firstName')
    last_name: str = Field(alias='lastName')
    email: str = Field(allow_mutation=False)
    created_at: datetime = Field(alias='createdAt', allow_mutation=False)

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True


class Profile(BaseUser):
    tenant: str
    roles: list[Role]
    licenses: list[Licence]


class ProfileResponse(Response[Profile]):
    pass


class User(BaseUser):
    is_enabled: Optional[bool] = Field(alias='isEnabled', allow_mutation=False)
    username: str = Field(alias='userName', allow_mutation=False)
    alias: Optional[str] = Field(alias='alias')
    country: str = Field(alias='country')
    organization: str = Field(alias='organization')
    last_login_at: Optional[datetime] = Field(alias='lastLoginAt', allow_mutation=False)
    _picture: Optional[File] = PrivateAttr(default=None)
    _groups: list['Group'] = PrivateAttr(default=[])
    _roles: list[Role] = PrivateAttr(default=[])
    _relationships: dict[str, Any] = PrivateAttr(default={})

    def set_relationships(self, value: dict) -> None:
        self._relationships = value

    @property
    def roles(self) -> list[Role]:
        if self._roles:
            return self._roles
        self._roles = [Role.get(role['id']) for role in self._relationships['roles']['data']]
        return self._roles

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'users'

    @staticmethod
    def get(user_id: str) -> 'User':
        """Get user by id from the scope

        Returns:
            User
        """
        log.debug('Get user: %s', user_id)

        api = SignalsNotebookApi.get_default_api()
        response = api.call(
            method='GET',
            path=('users', user_id),
        )
        result = UserResponse(**response.json())

        user = cast(ResponseData, result.data).body
        user.set_relationships(result.data.relationships)  # type: ignore

        log.debug('Role: %s was got successfully.', user_id)

        return user

    @staticmethod
    def get_list(q: str = '', enabled: bool = True, offset: int = 0, limit: int = 20) -> Generator['User', None, None]:
        """Get all users from the scope

        Parameter 'q' is a String and it is used to filter users.

        Example usage: Input 'foo' as value of 'q', will return
        Users whose first name starts with 'foo'.
        Users whose last name starts with 'foo'.
        Users whose email address starts with 'foo'.
        Users who has role name (except "Standard User") contains 'foo'.
        All of above are case insensitive.

        Args:
            q: query string for list users
            enabled: filter activated and deactivated users
            offset: Number of items to skip before returning the results.
            limit: Maximum number of items to return.

        Returns:
            User
        """
        api = SignalsNotebookApi.get_default_api()

        log.debug('Get List of Users')

        response = api.call(
            method='GET',
            path=('users',),
            params={
                'q': q,
                'enabled': json.dumps(enabled),
                'offset': offset,
                'limit': limit,
            },
        )
        result = UserResponse(**response.json())

        for item in result.data:
            user = cast(ResponseData, item).body
            user.set_relationships(item.relationships)  # type: ignore

            yield user

        while result.links and result.links.next:
            response = api.call(
                method='GET',
                path=result.links.next,
            )

            result = UserResponse(**response.json())

            for item in result.data:
                user = cast(ResponseData, item).body
                user.set_relationships(item.relationships)  # type: ignore

                yield user

        log.debug('List of Users was got successfully.')

    @staticmethod
    def get_current_user() -> Profile:
        """Get current user for api session

        Returns:
            User
        """
        api = SignalsNotebookApi.get_default_api()

        log.debug('Get current user')

        response = api.call(
            method='GET',
            path=('profiles', 'me'),
        )
        result = ProfileResponse(**response.json())

        log.debug('Current user was got successfully.')

        return cast(ResponseData, result.data).body

    @classmethod
    def create(
        cls,
        alias: str,
        country: str,
        email: str,
        first_name: str,
        last_name: str,
        organization: str,
        roles: Optional[list[Role]],
    ) -> 'User':
        """Create new User

        Returns:
            User
        """
        api = SignalsNotebookApi.get_default_api()

        log.debug('Create User: %s...', cls.__name__)

        response = api.call(
            method='POST',
            path=(cls._get_endpoint(),),
            json={
                'data': {
                    'attributes': {
                        'alias': alias,
                        'country': country,
                        'emailAddress': email,
                        'firstName': first_name,
                        'lastName': last_name,
                        'organization': organization,
                        'roles': [role.dict(include={'id', 'name'}) for role in roles] if roles else None,
                    },
                }
            },
        )

        result = UserResponse(**response.json())

        user = cast(ResponseData, result.data).body
        user.set_relationships(result.data.relationships)  # type: ignore

        log.debug('User: %s was created.', cls.__name__)

        return user

    def refresh(self) -> None:
        """Refresh user with new changes values

        Returns:

        """
        refreshed_entity = self.get(self.id)
        for field in self.__fields__.values():
            if field.field_info.allow_mutation:
                new_value = getattr(refreshed_entity, field.name)
                setattr(self, field.name, new_value)

    def save(self) -> None:
        """Update attributes of a specified user.

        Returns:

        """
        api = SignalsNotebookApi.get_default_api()
        api.call(
            method='PATCH',
            path=(
                self._get_endpoint(),
                self.id,
            ),
            json={
                'data': {
                    'attributes': self.dict(
                        by_alias=True,
                        include={
                            'alias',
                            'country',
                            'first_name',
                            'last_name',
                            'organization',
                        },
                    )
                },
            },
        )
        log.debug('User: %s was saved successfully', self.id)

    def delete(self) -> None:
        """Make specified user disabled.

        Returns:

        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Disable User: %s...', self.id)

        api.call(
            method='DELETE',
            path=(self._get_endpoint(), self.id),
        )
        log.debug('User: %s was disabled successfully', self.id)

    @property
    def picture(self) -> Optional[File]:
        if self._picture:
            return self._picture

        api = SignalsNotebookApi.get_default_api()
        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.id, 'picture'),
        )
        if response.content == b'':
            return self._picture

        content_disposition = response.headers.get('content-disposition', '')
        content_type = response.headers.get('content-type', '')
        extension = mimetypes.guess_extension(content_type)

        _, params = cgi.parse_header(content_disposition)
        file_name = f'{self.first_name}_{self.last_name}{extension}'
        self._picture = File(name=file_name, content=response.content, content_type=content_type)
        return self._picture

    @property
    def groups(self) -> list['Group']:
        from signals_notebook.users.group import GroupResponse

        if self._groups:
            return self._groups

        api = SignalsNotebookApi.get_default_api()

        log.debug('Getting System Groups')

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.id, 'systemGroups'),
        )
        result = GroupResponse(**response.json())

        log.debug('List of groups was got successfully.')

        return [cast(ResponseData, item).body for item in result.data]


class UserResponse(Response[User]):
    pass
