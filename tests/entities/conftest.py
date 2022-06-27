import pytest
from pytest_factoryboy import register

from tests.entities.factories import (
    BiologicalSequenceFactory,
    ChemicalDrawingFactory,
    EIDFactory,
    EntityFactory,
    ExcelFactory,
    ExperimentFactory,
    ImageFactory,
    NotebookFactory,
    PowerPointFactory,
    TextFactory,
    WordFactory,
)
from tests.entities.samples.factories import (
    SampleFactory,
    SamplePropertyFactory,
    SamplesContainerFactory,
)
from tests.entities.stoichiometry.factories import StoichiometryFactory
from tests.entities.tables.factories import TableFactory
from tests.entities.todo_list.factories import TaskFactory, TaskPropertyFactory, TodoListFactory


register(EIDFactory)
register(NotebookFactory)
register(ExperimentFactory)
register(TextFactory)
register(ChemicalDrawingFactory)
register(ImageFactory)
register(TableFactory)
register(StoichiometryFactory)
register(EntityFactory)
register(WordFactory)
register(ExcelFactory)
register(BiologicalSequenceFactory)
register(SamplesContainerFactory)
register(SampleFactory)
register(SamplePropertyFactory)
register(PowerPointFactory)
register(TodoListFactory)
register(TaskFactory)
register(TaskPropertyFactory)


@pytest.fixture()
def entity_store_mock(mocker):
    return mocker.patch('signals_notebook.entities.EntityStore')
