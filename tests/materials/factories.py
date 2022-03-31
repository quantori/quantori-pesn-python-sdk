import factory

from signals_notebook.materials import Asset
from signals_notebook.types import MaterialType, MID


class MIDFactory(factory.Factory):
    class Meta:
        model = MID

    id = factory.Faker('md5')
    type = factory.Iterator(MaterialType)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        _id = kwargs.get('id')
        _type = kwargs.get('type')
        return model_class(f'{_type}:{_id}')


class AssetFactory(factory.Factory):
    class Meta:
        model = Asset

    assetTypeId = factory.Faker('md5')
    library = factory.Faker('word')
    eid = factory.SubFactory(MIDFactory)
    name = factory.Faker('word')
    description = factory.Faker('text')
    digest = factory.Sequence(lambda n: f'{n}')
    createdAt = factory.Faker('date_time')
    editedAt = factory.Faker('date_time')
