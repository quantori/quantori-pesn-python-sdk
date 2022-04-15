import factory

from signals_notebook.common_types import MaterialType, MID
from signals_notebook.materials import Asset, Batch, Library


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


class BaseMaterialEntityFactory(factory.Factory):
    class Meta:
        abstract = True

    asset_type_id = factory.Faker('md5')
    library = factory.Faker('word')
    eid = factory.SubFactory(MIDFactory)
    name = factory.Faker('word')
    description = factory.Faker('text')
    digest = factory.Sequence(lambda n: f'{n}')
    created_at = factory.Faker('date_time')
    edited_at = factory.Faker('date_time')


class LibraryFactory(BaseMaterialEntityFactory):
    class Meta:
        model = Library

    type = MaterialType.LIBRARY
    name = factory.LazyAttribute(lambda o: o.library)


class AssetFactory(BaseMaterialEntityFactory):
    class Meta:
        model = Asset

    type = MaterialType.ASSET


class BatchFactory(BaseMaterialEntityFactory):
    class Meta:
        model = Batch

    type = MaterialType.BATCH
