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
