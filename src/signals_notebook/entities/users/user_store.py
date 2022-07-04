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
        return cast(ResponseData, result.data).body

    @classmethod
    def get_list(cls) -> Generator[User, None, None]:
        """Get all users from the scope

        Returns:
            User
        """
        api = SignalsNotebookApi.get_default_api()
        response = api.call(
            method='GET',
            path=('users',),
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
