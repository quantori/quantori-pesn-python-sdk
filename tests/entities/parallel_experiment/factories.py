from signals_notebook.common_types import EntityType
from signals_notebook.entities.parallel_experiment.cell import SubExperimentSummaryCell
from signals_notebook.entities.parallel_experiment.parallel_experiment import ParallelExperiment
from signals_notebook.entities.parallel_experiment.row import Row
from signals_notebook.entities.parallel_experiment.sub_experiment import SubExperiment
from signals_notebook.entities.parallel_experiment.sub_experiment_layout import SubExperimentLayout
from signals_notebook.entities.parallel_experiment.sub_experiment_summary import SubExperimentSummary
from tests.entities.factories import EntityFactory


class ParallelExperimentFactory(EntityFactory):
    class Meta:
        model = ParallelExperiment

    type = EntityType.PARALLEL_EXPERIMENT


class SubExperimentFactory(EntityFactory):
    class Meta:
        model = SubExperiment

    type = EntityType.SUB_EXPERIMENT


class SubExperimentSummaryFactory(EntityFactory):
    class Meta:
        model = SubExperimentSummary

    type = EntityType.SUB_EXPERIMENT_SUMMARY


class SubExperimentSummaryCellFactory(EntityFactory):
    class Meta:
        model = SubExperimentSummaryCell


class SubExperimentSummaryRowFactory(EntityFactory):
    class Meta:
        model = Row


class SubExperimentLayoutFactory(EntityFactory):
    class Meta:
        model = SubExperimentLayout

    type = EntityType.SUB_EXPERIMENT_LAYOUT
