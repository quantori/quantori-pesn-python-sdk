import factory

from signals_notebook.common_types import EntityType, ObjectType
from signals_notebook.entities import Sample, SamplesContainer
from signals_notebook.entities.samples.sample import SampleCell
from tests.entities.factories import EntityFactory


class SamplesContainerFactory(EntityFactory):
    class Meta:
        model = SamplesContainer

    type = EntityType.SAMPLES_CONTAINER


class SampleFactory(EntityFactory):
    class Meta:
        model = Sample

    type = EntityType.SAMPLE


class SampleCellFactory(factory.Factory):
    id = factory.Faker('word')
    type = ObjectType.PROPERTY
    content = factory.Dict({'value': 4})

    class Meta:
        model = SampleCell
