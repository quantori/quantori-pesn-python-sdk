import factory

from signals_notebook.entities import Experiment, Notebook, Text
from signals_notebook.types import EID, EntityType


class EIDFactory(factory.Factory):
    class Meta:
        model = EID

    id = factory.Faker('uuid4')
    type = factory.Iterator(EntityType)

    @classmethod
    def _create(cls, model_class, id, type):
        return model_class(f'{type}:{id}')


class EntityFactory(factory.Factory):
    class Meta:
        abstract = True

    eid = factory.SubFactory(EIDFactory) # factory.LazyAttribute(lambda o: f'{EntityType.NOTEBOOK}:{o.uuid}')
    name = factory.Faker('word')
    description = factory.Faker('text')
    digest = factory.Sequence(lambda n: f'{n}')
    createdAt = factory.Faker('date_time')
    editedAt = factory.Faker('date_time')


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

