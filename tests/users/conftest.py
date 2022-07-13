import pytest
from pytest_factoryboy import register

from tests.users.factories import (
    GroupFactory,
    LicenceFactory,
    ProfileFactory,
    RoleFactory,
    UserFactory,
)


register(UserFactory)
register(RoleFactory)
register(LicenceFactory)
register(ProfileFactory)
register(GroupFactory)


@pytest.fixture()
def get_response_object(mocker):
    def _f(response):
        mock = mocker.Mock()
        mock.json.return_value = response
        return mock

    return _f