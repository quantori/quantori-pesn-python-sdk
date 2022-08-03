import factory

from signals_notebook.common_types import EntityType
from signals_notebook.entities.parallel_experiment.sub_experiment import SubExperiment
from signals_notebook.entities.parallel_experiment.parallel_experiment import ParallelExperiment
from tests.entities.factories import EntityFactory


# class SamplesContainerFactory(EntityFactory):
#     class Meta:
#         model = SamplesContainer
#
#     type = EntityType.SAMPLES_CONTAINER
#
#
# class SampleFactory(EntityFactory):
#     class Meta:
#         model = Sample
#
#     type = EntityType.SAMPLE
#
#
# class SampleCellFactory(factory.Factory):
#     id = factory.Faker('word')
#     type = ObjectType.PROPERTY
#     content = factory.Dict({'value': 4})
#
#     class Meta:
#         model = SampleCell


class ParallelExperimentFactory(EntityFactory):
    class Meta:
        model = ParallelExperiment

    type = EntityType.PARALLEL_EXPERIMENT


class SubExperimentFactory(EntityFactory):
    class Meta:
        model = SubExperiment

    type = EntityType.SUB_EXPERIMENT