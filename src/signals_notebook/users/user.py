import cgi
import logging
import mimetypes
from datetime import datetime
from typing import cast, Optional

from pydantic import BaseModel, Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import File, Response, ResponseData
from signals_notebook.users.group import Group, GroupResponse
from signals_notebook.users.profile import Role

log = logging.getLogger(__name__)


class User(BaseModel):
    is_enabled: Optional[bool] = Field(alias='isEnabled', allow_mutation=False)
    id: str = Field(alias='userId', allow_mutation=False)
    username: str = Field(alias='userName', allow_mutation=False)
    email: str = Field(allow_mutation=False)
    alias: Optional[str] = Field(alias='alias')
    first_name: str = Field(alias='firstName')
    last_name: str = Field(alias='lastName')
    country: str = Field(alias='country')
    organization: str = Field(alias='organization')
    created_at: datetime = Field(alias='createdAt', allow_mutation=False)
    last_login_at: Optional[datetime] = Field(alias='lastLoginAt', allow_mutation=False)
    _picture: Optional[File] = PrivateAttr(default=None)
    _groups: list[Group] = PrivateAttr(default=[])
    _roles: list[Role] = PrivateAttr(default=[])
    _relationships: dict = PrivateAttr(default={})

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True

    def set_relationships(self, value: dict) -> None:
        self._relationships = value

    @property
    def roles(self) -> list[Role]:
        if self._roles:
            return self._roles
        self._roles = [Role.get(i['id']) for i in self._relationships['roles']['data']]
        return self._roles

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'users'

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
        log.debug('User: %s was created.', cls.__name__)

        result = UserResponse(**response.json())
        return cast(ResponseData, result.data).body

    def refresh(self) -> None:
        """Refresh user with new changes values

        Returns:

        """
        from signals_notebook.users.user_store import UserStore

        UserStore.refresh(self)

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

    def delete(self):
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
    def groups(self) -> list[Group]:
        if self._groups:
            return self._groups

        api = SignalsNotebookApi.get_default_api()
        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.id, 'systemGroups'),
        )
        result = GroupResponse(**response.json())
        return [cast(ResponseData, item).body for item in result.data]


class UserResponse(Response[User]):
    pass