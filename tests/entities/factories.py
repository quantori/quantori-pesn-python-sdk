import factory

from signals_notebook.common_types import EID, EntityType, ObjectType
from signals_notebook.entities import (
    BiologicalSequence,
    ChemicalDrawing,
    Entity,
    Excel,
    Experiment,
    Image,
    Notebook,
    PowerPoint,
    Spotfire,
    Text,
    Word,
)
from signals_notebook.users import (
    Group,
    Licence,
    Profile,
    Role,
    User,
    Privelege,
)


class EIDFactory(factory.Factory):
    class Meta:
        model = EID

    id = factory.Faker('uuid4')
    type = factory.Iterator(EntityType)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        _id = kwargs.get('id')
        _type = kwargs.get('type')
        return model_class(f'{_type}:{_id}')


class EntityFactory(factory.Factory):
    class Meta:
        model = Entity

    eid = factory.SubFactory(EIDFactory)
    type = factory.Faker('word')
    name = factory.Faker('word')
    description = factory.Faker('text')
    digest = factory.Sequence(lambda n: f'{n}')
    created_at = factory.Faker('date_time')
    edited_at = factory.Faker('date_time')


class NotebookFactory(EntityFactory):
    class Meta:
        model = Notebook

    type = EntityType.NOTEBOOK


class ExperimentFactory(EntityFactory):
    class Meta:
        model = Experiment

    type = EntityType.EXPERIMENT


class TextFactory(EntityFactory):
    class Meta:
        model = Text

    type = EntityType.TEXT


class ChemicalDrawingFactory(EntityFactory):
    class Meta:
        model = ChemicalDrawing

    type = EntityType.CHEMICAL_DRAWING


class ImageFactory(EntityFactory):
    class Meta:
        model = Image

    type = EntityType.IMAGE_RESOURCE


class WordFactory(EntityFactory):
    class Meta:
        model = Word

    type = EntityType.WORD


class ExcelFactory(EntityFactory):
    class Meta:
        model = Excel

    type = EntityType.EXCEL


class BiologicalSequenceFactory(EntityFactory):
    class Meta:
        model = BiologicalSequence

    type = EntityType.BIO_SEQUENCE


class PowerPointFactory(EntityFactory):
    class Meta:
        model = PowerPoint

    type = EntityType.POWER_POINT


class SpotfireFactory(EntityFactory):
    class Meta:
        model = Spotfire

    type = EntityType.SPOTFIRE


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
