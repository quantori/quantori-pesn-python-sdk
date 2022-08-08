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
    MaterialTableFactory,
    NotebookFactory,
    PowerPointFactory,
    RequestFactory,
    SpotfireFactory,
    TextFactory,
    UploadedResourceFactory,
    WordFactory,
)
from tests.entities.plates.factories import PlateContainerFactory
from tests.entities.samples.factories import (
    SampleCellFactory,
    SampleFactory,
    SamplesContainerFactory,
)
from tests.entities.stoichiometry.factories import StoichiometryFactory
from tests.entities.tables.factories import TableFactory
from tests.entities.todo_list.factories import TaskCellFactory, TaskContainerFactory, TaskFactory, TodoListFactory

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
register(SampleCellFactory)
register(PowerPointFactory)
register(SpotfireFactory)
register(TodoListFactory)
register(TaskFactory)
register(TaskCellFactory)
register(UploadedResourceFactory)
register(PlateContainerFactory)
register(MaterialTableFactory)
register(RequestFactory)
register(TaskContainerFactory)


@pytest.fixture()
def entity_store_mock(mocker):
    return mocker.patch('signals_notebook.entities.EntityStore')


@pytest.fixture()
def get_response_object(mocker):
    def _f(response):
        mock = mocker.Mock()
        mock.json.return_value = response
        return mock

    return _f
