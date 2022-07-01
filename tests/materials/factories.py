import factory

from signals_notebook.common_types import File, MaterialType, MID
from signals_notebook.materials import Asset, Batch, Library
from signals_notebook.materials.field import AssetConfig, BatchConfig, MaterialFieldType, Numbering


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

    @factory.post_generation
    def _asset_config(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self._asset_config = extracted
        else:
            self._asset_config = AssetConfig(
                numbering=Numbering(format='AST-###'),
                fields=[
                    {
                        'id': '123',
                        'name': 'Name',
                        'mandatory': True,
                        'hidden': False,
                        'dataType': MaterialFieldType.TEXT,
                    }
                ],
                display_name='Asset',
                asset_name_field_id='Name',
            )

    @factory.post_generation
    def _batch_config(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self._batch_config = extracted
        else:
            self._batch_config = BatchConfig(
                numbering=Numbering(format='LOT-###'),
                fields=[
                    {
                        'id': '123',
                        'name': 'Name',
                        'mandatory': True,
                        'hidden': False,
                        'dataType': MaterialFieldType.TEXT,
                    },
                    {
                        'id': '456',
                        'name': 'Link Name',
                        'mandatory': True,
                        'hidden': False,
                        'dataType': MaterialFieldType.LINK,
                    },
                ],
                display_name='Lot',
            )


class AssetFactory(BaseMaterialEntityFactory):
    class Meta:
        model = Asset

    type = MaterialType.ASSET
    _library = factory.SubFactory(LibraryFactory)


class BatchFactory(BaseMaterialEntityFactory):
    class Meta:
        model = Batch

    type = MaterialType.BATCH
    _library = factory.SubFactory(LibraryFactory)


class FileFactory(factory.Factory):
    class Meta:
        model = File

    name = factory.Faker('word')
