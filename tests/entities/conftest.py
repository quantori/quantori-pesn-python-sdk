import pytest
from pytest_factoryboy import register

from tests.entities.factories import (
    ChemicalDrawingFactory,
    EIDFactory,
    ExperimentFactory,
    ImageFactory,
    NotebookFactory,
    TextFactory,
)

register(EIDFactory)
register(NotebookFactory)
register(ExperimentFactory)
register(TextFactory)
register(ChemicalDrawingFactory)
register(ImageFactory)


@pytest.fixture()
def api_mock(mocker):
    return mocker.Mock()


@pytest.fixture(autouse=True)
def signals_notebook_api_mock(mocker, api_mock):
    return mocker.patch('signals_notebook.entities.entity.SignalsNotebookApi.get_default_api', return_value=api_mock)


@pytest.fixture()
def entity_store_mock(mocker):
    return mocker.patch('signals_notebook.entities.EntityStore')
