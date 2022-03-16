import pytest
from pytest_factoryboy import register

from tests.entities.factories import ExperimentFactory, NotebookFactory, TextFactory

register(NotebookFactory)
register(ExperimentFactory)
register(TextFactory)


@pytest.fixture()
def api_mock(mocker):
    return mocker.Mock()


@pytest.fixture(autouse=True)
def signals_notebook_api_mock(mocker, api_mock):
    return mocker.patch('signals_notebook.entities.entity.SignalsNotebookApi.get_default_api', return_value=api_mock)


@pytest.fixture()
def entity_store_mock(mocker):
    return mocker.patch('signals_notebook.entities.EntityStore')
