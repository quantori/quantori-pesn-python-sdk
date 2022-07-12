import factory

from signals_notebook.common_types import ObjectType
from signals_notebook.users.group import Group
from signals_notebook.users.profile import Licence, Privelege, Profile, Role
from signals_notebook.users.user import User
from tests.entities.factories import EIDFactory


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.SubFactory(EIDFactory)
    username = factory.Faker('word')
    email = factory.Faker('email')
    first_name = factory.Faker('word')
    last_name = factory.Faker('word')
    country = factory.Faker('word')
    organization = factory.Faker('word')
    created_at = factory.Faker('date_time')


class PrivilegeFactory(factory.Factory):
    class Meta:
        model = Privelege


class RoleFactory(factory.Factory):
    class Meta:
        model = Role

    id = factory.Faker('uuid4')
    name = factory.Faker('word')
    description = factory.Faker('word')
    privileges = factory.SubFactory(PrivilegeFactory)


class LicenceFactory(factory.Factory):
    class Meta:
        model = Licence

    id = factory.SubFactory(EIDFactory)
    name = factory.Faker('word')
    expires_at = factory.Faker('date_time')
    valid = factory.Faker('pybool')
    has_service_expired = factory.Faker('pybool')
    has_user_found = factory.Faker('pybool')
    has_user_activated = factory.Faker('pybool')


class ProfileFactory(factory.Factory):
    class Meta:
        model = Profile

    id = factory.SubFactory(EIDFactory)
    email = factory.Faker('email')
    first_name = factory.Faker('word')
    last_name = factory.Faker('word')
    tenant = factory.Faker('word')
    created_at = factory.Faker('date_time')
    roles = factory.List([factory.SubFactory(RoleFactory) for _ in range(1)])
    licenses = factory.List([factory.SubFactory(LicenceFactory) for _ in range(1)])


class GroupFactory(factory.Factory):
    class Meta:
        model = Group

    type = ObjectType.GROUP
    id = factory.SubFactory(EIDFactory)
    is_system = factory.Faker('pybool')
    name = factory.Faker('word')
    description = factory.Faker('word')
    created_at = factory.Faker('date_time')
    edited_at = factory.Faker('date_time')
    digest = factory.Faker('word')
