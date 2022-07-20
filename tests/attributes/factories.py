import factory

from signals_notebook.attributes import Attribute, AttributeOption
from signals_notebook.common_types import AttrID, ObjectType


class AttrIDFactory(factory.Factory):
    class Meta:
        model = AttrID

    id = factory.Sequence(lambda n: n + 1)
    type = ObjectType.ATTRIBUTE

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        _id = kwargs.get('id')
        _type = kwargs.get('type')
        return model_class(f'{_type}:{_id}')


class AttributeFactory(factory.Factory):
    id = factory.SubFactory(AttrIDFactory)
    type = 'choice'
    name = factory.Faker('word')
    options = factory.LazyAttribute(lambda o: [f'{o.name} {i}' for i in range(3)])

    class Meta:
        model = Attribute


class AttributeOptionFactory(factory.Factory):
    id = factory.Sequence(lambda n: n + 1)
    key = factory.Faker('word')
    value = factory.Faker('word')

    class Meta:
        model = AttributeOption
