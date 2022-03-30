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
def entity_store_mock(mocker):
    return mocker.patch('signals_notebook.entities.EntityStore')
