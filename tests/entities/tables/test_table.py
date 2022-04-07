import json
import os.path
from uuid import UUID

import pandas as pd
import pytest

from signals_notebook.common_types import EntityType, ObjectType
from signals_notebook.entities.tables.cell import ColumnDefinition
from signals_notebook.entities.tables.row import Row


DIGEST = '123'


@pytest.fixture()
def table(table_factory):
    return table_factory(eid__type=EntityType.GRID)


@pytest.fixture()
def table_with_digest(eid_factory, table_factory):
    eid = eid_factory(type=EntityType.GRID)
    return table_factory(eid=eid, digest=DIGEST)


@pytest.fixture()
def reload_data_response():
    path = os.path.join(os.path.dirname(__file__), 'reload_data_response.json')
    with open(path, 'r') as f:
        response = json.load(f)

    return response


@pytest.fixture()
def reload_data_response_square_table():
    path = os.path.join(os.path.dirname(__file__), 'reload_data_response_square_table.json')
    with open(path, 'r') as f:
        response = json.load(f)

    return response


@pytest.fixture()
def column_definitions_response(table):
    return {
        'links': {'self': f'https://example.com/{table.eid}'},
        'data': {
            'type': ObjectType.COLUMN_DEFINITIONS,
            'id': table.eid,
            'attributes': {
                'id': table.eid,
                'type': ObjectType.COLUMN_DEFINITIONS,
                'columns': [
                    {'key': 'fac1b3c0-c262-4b47-92c2-5f6535536ca3', 'title': 'Column 1', 'type': 'text', 'saved': True},
                    {'key': '15c9d0ef-3873-481f-bb1b-5d719bde0598', 'title': 'Column 2', 'type': 'text', 'saved': True},
                ],
            },
        },
    }


@pytest.fixture()
def all_column_types_definitions_response():
    path = os.path.join(os.path.dirname(__file__), 'all_column_types_definitions_response.json')
    with open(path, 'r') as f:
        response = json.load(f)

    return response


def test_reload_data(api_mock, reload_data_response, table):
    api_mock.call.return_value.json.return_value = reload_data_response

    table._reload_data()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('adt', table.eid),
        params={
            'value': 'normalized',
        },
    )

    assert len(table._rows) == len(reload_data_response['data'])
    assert len(table._rows_by_id) == len(reload_data_response['data'])

    for row in table:
        assert isinstance(row, Row)


def test_get_column_definitions_list(api_mock, all_column_types_definitions_response, table):
    api_mock.call.return_value.json.return_value = all_column_types_definitions_response

    result = table.get_column_definitions_list()
    columns = all_column_types_definitions_response['data']['attributes']['columns']

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('adt', table.eid, '_column'),
    )

    assert len(result) == len(columns)

    for i in range(len(columns)):
        assert isinstance(result[i], ColumnDefinition)
        assert str(result[i].key) == columns[i]['key']
        assert result[i].title == columns[i]['title']
        assert result[i].type == columns[i]['type']
        assert result[i].saved == columns[i]['saved']


def test_get_column_definitions_map(api_mock, all_column_types_definitions_response, table):
    api_mock.call.return_value.json.return_value = all_column_types_definitions_response

    result = table.get_column_definitions_map()
    columns = all_column_types_definitions_response['data']['attributes']['columns']

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('adt', table.eid, '_column'),
    )

    assert len(result) == len(columns) * 2
    for column in columns:
        assert column['key'] in result
        assert column['title'] in result


def test_as_dataframe(api_mock, reload_data_response, table):
    api_mock.call.return_value.json.return_value = reload_data_response

    result = table.as_dataframe()
    rows = reload_data_response['data']
    columns = reload_data_response['included'][1]['attributes']['columns']

    assert isinstance(result, pd.DataFrame)
    assert len(rows) == result.shape[0]
    assert len(columns) == result.shape[1]


def test_as_raw_data(api_mock, reload_data_response, table):
    api_mock.call.return_value.json.return_value = reload_data_response

    result = table.as_raw_data()
    rows = reload_data_response['data']
    columns = reload_data_response['included'][1]['attributes']['columns']

    assert isinstance(result, list)
    assert len(result) == len(rows)
    assert isinstance(result[0], dict)
    assert len(result[0]) == len(columns)


@pytest.mark.parametrize(
    'index', [0, '945e5287-1e1f-4310-b42a-43ed0405a4b4', UUID('945e5287-1e1f-4310-b42a-43ed0405a4b4')]
)
def test_getitem(api_mock, reload_data_response, table, index):
    api_mock.call.return_value.json.return_value = reload_data_response

    assert isinstance(table[index], Row)


def test_getitem_with_invalid_index(api_mock, reload_data_response, table):
    api_mock.call.return_value.json.return_value = reload_data_response

    with pytest.raises(IndexError) as e:
        table[1.5]

    assert str(e.value) == 'Invalid index'


def test_iter(api_mock, reload_data_response, table):
    api_mock.call.return_value.json.return_value = reload_data_response

    for row in table:
        assert isinstance(row, Row)


@pytest.mark.parametrize('digest, force', [(DIGEST, False), (None, True)])
def test_delete_row_by_id(api_mock, reload_data_response, table, digest, force):
    api_mock.call.return_value.json.return_value = reload_data_response
    row_id = reload_data_response['data'][0]['id']

    table.delete_row_by_id(row_id=row_id, digest=digest, force=force)

    api_mock.call.assert_any_call(
        method='DELETE',
        path=('adt', table.eid, row_id),
        params={
            'digest': digest,
            'force': 'true' if force else 'false',
        },
    )


def test_add_row(api_mock, column_definitions_response, table):
    api_mock.call.return_value.json.return_value = column_definitions_response

    assert len(table._rows) == 0

    table.add_row({'Column 1': dict(value='Text 1'), 'Column 2': dict(value='Text 2')})

    assert len(table._rows) == 1
    assert table._rows[0].cells[0].value == 'Text 1'
    assert table._rows[0].cells[1].value == 'Text 2'


@pytest.mark.parametrize('digest, force', [(DIGEST, False), (None, True)])
def test_save_after_add_rows(
    api_mock, column_definitions_response, reload_data_response_square_table, table_with_digest, digest, force
):
    api_mock.call.return_value.json.return_value = column_definitions_response
    column_1_id = column_definitions_response['data']['attributes']['columns'][0]['key']
    column_2_id = column_definitions_response['data']['attributes']['columns'][1]['key']

    table_with_digest.add_row({'Column 1': dict(value='Text 1'), 'Column 2': dict(value='Text 2')})
    table_with_digest.add_row({'Column 1': dict(value='Temp 1'), 'Column 2': dict(value='Temp 2')})

    api_mock.call.return_value.json.return_value = reload_data_response_square_table
    table_with_digest.save(force=force)

    api_mock.call.assert_any_call(
        method='PATCH',
        path=('entities', table_with_digest.eid, 'properties'),
        params={
            'digest': digest,
            'force': 'true' if force else 'false',
        },
        json={
            'data': [
                {'attributes': {'name': 'Name', 'value': table_with_digest.name}},
                {'attributes': {'name': 'Description', 'value': table_with_digest.description}},
            ],
        },
    )

    api_mock.call.assert_any_call(
        method='PATCH',
        path=('adt', table_with_digest.eid),
        params={
            'digest': digest,
            'force': 'true' if force else 'false',
        },
        data=json.dumps(
            {
                'data': [
                    {
                        'type': 'adtRow',
                        'attributes': {
                            'action': 'create',
                            'cells': [
                                {'key': column_1_id, 'content': {'value': 'Text 1'}},
                                {'key': column_2_id, 'content': {'value': 'Text 2'}},
                            ],
                        },
                    },
                    {
                        'type': 'adtRow',
                        'attributes': {
                            'action': 'create',
                            'cells': [
                                {'key': column_1_id, 'content': {'value': 'Temp 1'}},
                                {'key': column_2_id, 'content': {'value': 'Temp 2'}},
                            ],
                        },
                    },
                ]
            }
        ),
    )

    api_mock.call.assert_called_with(
        method='GET',
        path=('adt', table_with_digest.eid),
        params={
            'value': 'normalized',
        },
    )


@pytest.mark.parametrize('digest, force', [(DIGEST, False), (None, True)])
def test_save_after_change_cell_and_delete_row(
    api_mock, column_definitions_response, reload_data_response_square_table, table_with_digest, digest, force
):
    api_mock.call.return_value.json.return_value = column_definitions_response

    table_with_digest.add_row({'Column 1': dict(value='Text 1'), 'Column 2': dict(value='Text 2')})
    table_with_digest.add_row({'Column 1': dict(value='Temp 1'), 'Column 2': dict(value='Temp 2')})

    api_mock.call.return_value.json.return_value = reload_data_response_square_table
    reload_data = reload_data_response_square_table['data']
    table_with_digest.save(force=force)

    table_with_digest._rows[0].cells[0].set_value('Updated Text 1')
    table_with_digest._rows[1].delete()
    table_with_digest.save(force=force)

    api_mock.call.assert_any_call(
        method='PATCH',
        path=('entities', table_with_digest.eid, 'properties'),
        params={
            'digest': digest,
            'force': 'true' if force else 'false',
        },
        json={
            'data': [
                {'attributes': {'name': 'Name', 'value': table_with_digest.name}},
                {'attributes': {'name': 'Description', 'value': table_with_digest.description}},
            ],
        },
    )

    api_mock.call.assert_any_call(
        method='PATCH',
        path=('adt', table_with_digest.eid),
        params={
            'digest': digest,
            'force': 'true' if force else 'false',
        },
        data=json.dumps(
            {
                'data': [
                    {
                        'type': 'adtRow',
                        'id': reload_data[0]['id'],
                        'attributes': {
                            'action': 'update',
                            'cells': [
                                {
                                    'key': reload_data[0]['attributes']['cells'][0]['key'],
                                    'content': {'value': 'Updated Text 1'},
                                }
                            ],
                        },
                    },
                    {
                        'type': 'adtRow',
                        'id': reload_data[1]['id'],
                        'attributes': {'action': 'delete'},
                    },
                ]
            }
        ),
    )

    api_mock.call.assert_called_with(
        method='GET',
        path=('adt', table_with_digest.eid),
        params={
            'value': 'normalized',
        },
    )
