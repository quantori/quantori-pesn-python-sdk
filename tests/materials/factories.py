import factory

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
