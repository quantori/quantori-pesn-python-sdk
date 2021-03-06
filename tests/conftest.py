import pytest


@pytest.fixture()
def api_mock(mocker):
    return mocker.Mock()


@pytest.fixture(autouse=True)
def signals_notebook_api_mock(mocker, api_mock):
    return mocker.patch('signals_notebook.entities.entity.SignalsNotebookApi.get_default_api', return_value=api_mock)
