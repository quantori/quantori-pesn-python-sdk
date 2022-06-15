import factory

from signals_notebook.common_types import EntityType
from signals_notebook.entities import Sample, SamplesContainer
from signals_notebook.entities.samples.sample import SampleProperty
from tests.entities.factories import EntityFactory


class SamplesContainerFactory(EntityFactory):
    class Meta:
        model = SamplesContainer

    type = EntityType.SAMPLES_CONTAINER


class SampleFactory(EntityFactory):
    class Meta:
        model = Sample

    type = EntityType.SAMPLE


class SamplePropertyFactory(factory.Factory):
    id = factory.Faker('word')
    type = 'property'
    content = factory.Dict({'value': 4})

    class Meta:
        model = SampleProperty
