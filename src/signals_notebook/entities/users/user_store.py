import json
from typing import cast, Generator

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import ResponseData
from signals_notebook.entities.users.profile import Profile, ProfileResponse
from signals_notebook.entities.users.user import User, UserResponse


class UserStore:
    @classmethod
    def get(cls, user_id: str) -> User:
        """Get user by id from the scope

        Returns:
            User
        """
        api = SignalsNotebookApi.get_default_api()
        response = api.call(
            method='GET',
            path=('users', user_id),
        )
        result = UserResponse(**response.json())
        # user = cast(ResponseData, result.data).body
        # for i in response.json()['included']:
        #     if not user.roles:
        #         user.roles = []
        #     elif not user.groups:
        #         user.groups = []
        #     if i['type']=='role':
        #         user.roles.append(i['attributes'])
        #     if i['type']=='group':
        #         user.groups.append(i['attributes'])
        # return user
        return cast(ResponseData, result.data).body

    @classmethod
    def get_list(
        cls, q: str = '', enabled: bool = True, offset: int = 0, limit: int = 20
    ) -> Generator[User, None, None]:
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
        yield from [cast(ResponseData, item).body for item in result.data]

        while result.links and result.links.next:
            response = api.call(
                method='GET',
                path=result.links.next,
            )

            result = UserResponse(**response.json())  # type: ignore
            yield from [cast(ResponseData, item).body for item in result.data]

    @classmethod
    def get_current_user(cls) -> Profile:
        """Get current user for api session

        Returns:
            User
        """
        api = SignalsNotebookApi.get_default_api()
        response = api.call(
            method='GET',
            path=('profiles', 'me'),
        )
        result = ProfileResponse(**response.json())
        return cast(ResponseData, result.data).body

    @classmethod
    def refresh(cls, user: User) -> None:
        """Refresh Entity with new values

        Args:
            user: User

        Returns:

        """
        refreshed_entity = cls.get(user.id)
        for field in user.__fields__.values():
            if field.field_info.allow_mutation:
                new_value = getattr(refreshed_entity, field.name)
                setattr(user, field.name, new_value)
