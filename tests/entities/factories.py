import factory

from signals_notebook.entities import Experiment, Notebook
from signals_notebook.types import EntityType


class EntityFactory(factory.Factory):
    class Meta:
        abstract = True
        exclude = ('uuid', )

    uuid = factory.Faker('uuid4')
    eid = factory.LazyAttribute(lambda o: f'{EntityType.NOTEBOOK}{o.uuid}')
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

