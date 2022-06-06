from signals_notebook.common_types import EntityType
from signals_notebook.entities import SamplesContainer, Sample
from tests.entities.factories import EntityFactory


class SamplesContainerFactory(EntityFactory):
    class Meta:
        model = SamplesContainer

    type = EntityType.SAMPLES_CONTAINER


class SampleFactory(EntityFactory):
    class Meta:
        model = Sample

    type = EntityType.SAMPLE
