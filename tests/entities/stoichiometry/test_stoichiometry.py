import json
import os

import pytest

from signals_notebook.common_types import ChemicalDrawingFormat, EID, File
from signals_notebook.entities.stoichiometry.cell import ColumnDataType, ColumnDefinition
from signals_notebook.entities.stoichiometry.data_grid import DataGridKind
from signals_notebook.entities.stoichiometry.stoichiometry import Stoichiometry


@pytest.fixture()
def stoichiometry_data_response():
    path = os.path.join(os.path.dirname(__file__), 'stoichiometry_data_response.json')
    with open(path, 'r') as f:
        response = json.load(f)

    return response


@pytest.fixture()
def column_definitions_response():
    path = os.path.join(os.path.dirname(__file__), 'column_definitions_response.json')
    with open(path, 'r') as f:
        response = json.load(f)

    return response


@pytest.fixture()
def get_column_definitions_mock(mocker):
    column_definitions = [
        ColumnDefinition(key='id', title='ID', type=ColumnDataType.HTML),
        ColumnDefinition(key='name', title='Name', type=ColumnDataType.TEXT),
    ]
    return mocker.patch(
        'signals_notebook.entities.stoichiometry.stoichiometry.Stoichiometry.get_column_definitions',
        return_value=column_definitions,
    )


def test_fetch_data(api_mock, stoichiometry_data_response, get_column_definitions_mock):
    api_mock.call.return_value.json.return_value = stoichiometry_data_response
    entity_eid = stoichiometry_data_response['data']['id']

    stoichiometry = Stoichiometry.fetch_data(entity_eid)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('stoichiometry', entity_eid),
        params={
            'fields': 'reactants, products, solvents, conditions',
            'value': 'normalized',
        },
    )

    assert stoichiometry.eid == EID(entity_eid)
    assert len(stoichiometry.reactants._rows_by_id) == 2
    assert len(stoichiometry.products._rows_by_id) == 2
    assert len(stoichiometry.solvents._rows_by_id) == 1
    assert len(stoichiometry.conditions._rows_by_id) == 1
    assert len(stoichiometry.reactants.column_definitions) == 2
    assert len(stoichiometry.products.column_definitions) == 2
    assert len(stoichiometry.solvents.column_definitions) == 2
    assert len(stoichiometry.conditions.column_definitions) == 2


def test_fetch_data_list(api_mock, stoichiometry_data_response, get_column_definitions_mock):
    stoichiometry_data_response['data'] = [stoichiometry_data_response['data']]
    api_mock.call.return_value.json.return_value = stoichiometry_data_response
    entity_eid = stoichiometry_data_response['data'][0]['id']

    stoichiometry_list = Stoichiometry.fetch_data(entity_eid)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('stoichiometry', entity_eid),
        params={
            'fields': 'reactants, products, solvents, conditions',
            'value': 'normalized',
        },
    )

    assert len(stoichiometry_list) == 1

    stoichiometry = stoichiometry_list[0]

    assert stoichiometry.eid == EID(entity_eid)
    assert len(stoichiometry.reactants._rows_by_id) == 2
    assert len(stoichiometry.products._rows_by_id) == 2
    assert len(stoichiometry.solvents._rows_by_id) == 1
    assert len(stoichiometry.conditions._rows_by_id) == 1
    assert len(stoichiometry.reactants.column_definitions) == 2
    assert len(stoichiometry.products.column_definitions) == 2
    assert len(stoichiometry.solvents.column_definitions) == 2
    assert len(stoichiometry.conditions.column_definitions) == 2


def test_fetch_structure(api_mock, stoichiometry_factory):
    file_name = 'structure-1.cdxml'
    content = b'<?xml version="1.0" encoding="UTF-8" ?>'
    content_type = 'application/vnd.api+json; charset=utf-8'
    row_id = '1'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    stoichiometry = stoichiometry_factory()

    result = stoichiometry.fetch_structure(row_id=row_id, format=ChemicalDrawingFormat.CDXML)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('stoichiometry', stoichiometry.eid, row_id, 'structure'),
        params={
            'format': ChemicalDrawingFormat.CDXML,
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type


@pytest.mark.parametrize(
    'data_grid_kind, columns_count',
    [
        (DataGridKind.REACTANTS, 22),
        (DataGridKind.PRODUCTS, 19),
        (DataGridKind.SOLVENTS, 3),
        (DataGridKind.CONDITIONS, 3),
    ],
)
def test_get_column_definitions(
    api_mock, stoichiometry_factory, column_definitions_response, data_grid_kind, columns_count
):
    api_mock.call.return_value.json.return_value = column_definitions_response

    stoichiometry = stoichiometry_factory()

    result = stoichiometry.get_column_definitions(data_grid_kind=data_grid_kind)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('stoichiometry', stoichiometry.eid, 'columns', data_grid_kind),
    )

    assert len(result) == columns_count
    assert isinstance(result[0], ColumnDefinition)


def test_stoichiometry_get_html(api_mock, snapshot, stoichiometry_data_response, get_column_definitions_mock):
    api_mock.call.return_value.json.return_value = stoichiometry_data_response
    entity_eid = stoichiometry_data_response['data']['id']

    stoichiometry = Stoichiometry.fetch_data(entity_eid)

    stoichiometry_html = stoichiometry.get_html()

    snapshot.assert_match(stoichiometry_html)
