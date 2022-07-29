import json
import os.path
from uuid import UUID

import arrow
import pandas as pd
import pytest

from signals_notebook.common_types import EntityType, File, ObjectType
from signals_notebook.entities import Table, UploadedResource
from signals_notebook.entities.tables.cell import ColumnDataType, ColumnDefinition
from signals_notebook.entities.tables.row import Row

DIGEST = '123'


@pytest.fixture()
def get_response_object(mocker):
    def _f(response):
        mock = mocker.Mock()
        mock.json.return_value = response
        return mock

    return _f


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


@pytest.fixture()
def table_response():
    def wrapper(table_name: str):
        return {
            'links': {'self': 'https://ex.com/api/rest/v1.0/entities/grid:4df4e044-1b32-400f-81dd-571bb2adac9f'},
            'data': {
                'type': 'entity',
                'id': 'grid:4df4e044-1b32-400f-81dd-571bb2adac9f',
                'links': {'self': 'https://ex.com/api/rest/v1.0/entities/grid:4df4e044-1b32-400f-81dd-571bb2adac9f'},
                'attributes': {
                    'id': 'grid:4df4e044-1b32-400f-81dd-571bb2adac9f',
                    'eid': 'grid:4df4e044-1b32-400f-81dd-571bb2adac9f',
                    'name': table_name,
                    'description': '',
                    'createdAt': '2020-04-24T07:13:08.114Z',
                    'editedAt': '2020-04-24T07:13:08.114Z',
                    'type': 'grid',
                    'digest': '70068111',
                    'fields': {'Description': {'value': ''}, 'Name': {'value': 'frank-table-template-1'}},
                },
            },
        }

    return wrapper


@pytest.fixture()
def table_json_content():
    return (
        b'{"data": [{"ext_title": {"value": "3", "values": null, "type": null, "display": null}, '
        + b'"User Number Column": {"value": 234234.0, "values": null, "type": null, "display": "234234"}}]}'
    )


@pytest.fixture()
def table_csv_content():
    return (
        b'id,ext_title,ext_field1,User Number Column,User Column,SMTH ELSE'
        + os.linesep.encode('utf-8')
        + b',3,,234234,"3, 4",'
        + os.linesep.encode('utf-8')
        + b',,,234234,,edfsdf'
        + os.linesep.encode('utf-8')
        + b',5,,,,'
        + os.linesep.encode('utf-8')
        + b',,,,,sdfsdf'
    )


@pytest.fixture()
def properties():
    return {
        'links': {
            'self': 'https://example.com/api/rest/v1.0/entities/journal:111a8a0d-2772-47b0-b5b8-2e4faf04119e/properties'
        },
        'data': [
            {
                'type': 'property',
                'id': '3103',
                'meta': {
                    'definition': {
                        'type': 'text',
                        'attribute': {'id': '1', 'name': 'Text', 'type': 'text', 'counts': {'templates': {}}},
                    }
                },
                'attributes': {
                    'id': '3103',
                    'name': 'Name',
                    'value': 'Test creation by SDK',
                    'values': ['Test creation by SDK'],
                },
            },
            {
                'type': 'property',
                'id': '3102',
                'meta': {
                    'definition': {
                        'type': 'text',
                        'attribute': {'id': '1', 'name': 'Text', 'type': 'text', 'counts': {'templates': {}}},
                    }
                },
                'attributes': {
                    'id': '3102',
                    'name': 'Description',
                    'value': 'Created by Eugene Pokidov',
                    'values': ['Created by Eugene Pokidov'],
                },
            },
            {
                'type': 'property',
                'id': '3101',
                'meta': {
                    'definition': {
                        'type': 'date',
                        'attribute': {'id': '2', 'name': 'Date', 'type': 'date', 'counts': {'templates': {}}},
                    }
                },
                'attributes': {'id': '3101', 'name': 'My Notebook Field 1 (SK)', 'value': '', 'values': []},
            },
            {
                'type': 'property',
                'id': '3100',
                'meta': {
                    'definition': {
                        'type': 'text',
                        'attribute': {'id': '1', 'name': 'Text', 'type': 'text', 'counts': {'templates': {}}},
                    }
                },
                'attributes': {'id': '3100', 'name': 'My Notebook Field 2 (SK)', 'value': '', 'values': []},
            },
        ],
    }


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


@pytest.fixture()
def get_column_definitions_list_mock(mocker):
    column_definitions = [
        ColumnDefinition(key='49b2cf34-b4bb-4868-af67-931f31b46581', title='Col. Text', type=ColumnDataType.TEXT),
        ColumnDefinition(key='dff966b1-ed21-4f94-9446-78b00b01bdf8', title='Col. Date/Time', type=ColumnDataType.TEXT),
        ColumnDefinition(key='7dce6a7f-e491-4b70-8bf7-d6f342bedec7', title='Col. Number', type=ColumnDataType.NUMBER),
        ColumnDefinition(
            key='f0eb0e49-0460-4f84-8616-b17cebac69a3', title='Col. Number w/Uni', type=ColumnDataType.UNIT
        ),
        ColumnDefinition(
            key='ce8034b6-c29a-4027-b69b-b321a54c5f74', title='Col. Ext. Hyperlink', type=ColumnDataType.EXTERNAL_LINK
        ),
        ColumnDefinition(
            key='77f80aae-014b-4a1d-aaee-5c3b88a5dd66', title='Col. Autotext List', type=ColumnDataType.AUTOTEXT_LIST
        ),
        ColumnDefinition(
            key='cf27a778-9769-4d49-8d09-7fb68f0c7ca8', title='Col. Checkbox', type=ColumnDataType.BOOLEAN
        ),
        ColumnDefinition(
            key='1bdf51d0-08ab-4f56-9d51-4153d5feb228', title='Col. Internal Reference', type=ColumnDataType.LINK
        ),
        ColumnDefinition(key='e1f0fcb3-2319-47e7-af49-0ac9e6d66c6c', title='Col. List', type=ColumnDataType.LIST),
        ColumnDefinition(key='6ed558b6-7ba7-41a3-8f5e-0e16acb71f1c', title='Col. Integer', type=ColumnDataType.INTEGER),
        ColumnDefinition(
            key='c07d1a47-fad7-4ae0-b38c-8c7c25b49fa8', title='Col. Multi Select List', type=ColumnDataType.MULTI_SELECT
        ),
        ColumnDefinition(
            key='36ff8edc-e72e-40e2-a0d2-331b565fee90', title='Col. Attribute List', type=ColumnDataType.ATTRIBUTE_LIST
        ),
        ColumnDefinition(
            key='5b0b3a99-dc4f-4b3f-89d3-ed48c7adffe8',
            title='Col. Multi Attribute List',
            type=ColumnDataType.ATTRIBUTE_LIST,
        ),
    ]
    return mocker.patch(
        'signals_notebook.entities.tables.table.Table.get_column_definitions_list',
        return_value=column_definitions,
    )


def test_get_html(api_mock, get_column_definitions_list_mock, reload_data_response, table, snapshot):
    table.name = 'name'
    api_mock.call.return_value.json.return_value = reload_data_response

    table_html = table.get_html()

    snapshot.assert_match(table_html)


@pytest.mark.parametrize('digest, force', [(DIGEST, False), (None, True)])
def test_create_with_template_empty_table(api_mock, experiment_factory, table_factory, digest, force, table_response):
    template = table_factory()
    experiment = experiment_factory()
    table_name = 'SUPERDUPERPUPERTABLE'

    api_mock.call.return_value.json.return_value = table_response(table_name)
    table = Table.create(container=experiment, name=table_name, template=template.eid, digest=digest, force=force)

    request = {
        'data': {
            'type': EntityType.GRID,
            'attributes': {'name': table_name},
            'relationships': {
                'ancestors': {'data': [{'type': EntityType.EXPERIMENT, 'id': experiment.eid}]},
                'template': {'data': {'type': EntityType.GRID, 'id': template.eid}},
            },
        }
    }
    api_mock.call.assert_called_with(
        method='POST',
        path=('entities',),
        params={
            'digest': digest,
            'force': json.dumps(force),
        },
        json=request,
    )
    assert isinstance(table, Table)


@pytest.mark.parametrize('digest, force', [(DIGEST, False), (None, True)])
def test_create_with_template_full_table(
    api_mock,
    experiment_factory,
    table_factory,
    digest,
    force,
    table_response,
    table_json_content,
    get_response_object,
    column_definitions_response,
    reload_data_response_square_table,
    reload_data_response,
    properties,
):
    template = table_factory()
    experiment = experiment_factory()
    table_name = 'SUPERDUPERPUPERTABLE'
    response1 = table_response(table_name)
    response2 = column_definitions_response
    response3 = properties
    response4 = reload_data_response

    api_mock.call.side_effect = [
        get_response_object(response1),
        get_response_object(response2),
        get_response_object(response3),
        get_response_object(response3),
        get_response_object(reload_data_response_square_table),
        get_response_object(response4),
    ]

    table = Table.create(
        container=experiment,
        name=table_name,
        template=template.eid,
        digest=digest,
        force=force,
        content=table_json_content,
    )

    request = {
        'data': {
            'type': EntityType.GRID,
            'attributes': {'name': table_name},
            'relationships': {
                'ancestors': {'data': [{'type': EntityType.EXPERIMENT, 'id': experiment.eid}]},
                'template': {'data': {'type': EntityType.GRID, 'id': template.eid}},
            },
        }
    }
    api_mock.call.assert_any_call(
        method='POST',
        path=('entities',),
        params={
            'digest': digest,
            'force': json.dumps(force),
        },
        json=request,
    )
    assert isinstance(table, Table)
    assert table._rows != []
    assert table._rows_by_id != {}

    api_mock.call.assert_called_with(
        method='GET',
        path=('adt', table.eid),
        params={
            'value': 'normalized',
        },
    )


@pytest.mark.parametrize(
    'file_name, content_type',
    [
        ('file.csv', Table.ContentType.CSV),
        ('file.json', Table.ContentType.JSON),
    ],
)
def test_create_table_file(
    api_mock, experiment_factory, eid_factory, file_name, content_type, table_csv_content, table_json_content
):
    container = experiment_factory()
    eid = eid_factory(type=EntityType.UPLOADED_RESOURCE)
    content = table_json_content if content_type == Table.ContentType.JSON else table_csv_content
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'attributes': {
                'eid': eid,
                'name': file_name,
                'description': '',
                'type': EntityType.UPLOADED_RESOURCE,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '222',
            },
        },
    }
    api_mock.call.return_value.json.return_value = response
    result = Table.create(container=container, name=file_name, content=content, content_type=content_type, force=True)

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('entities', container.eid, 'children', file_name),
        params={
            'digest': None,
            'force': 'true',
        },
        headers={
            'Content-Type': content_type,
        },
        data=content,
    )

    assert isinstance(result, UploadedResource)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_get_content_csv(api_mock, table_factory, table_csv_content):
    table = table_factory(name='file')
    file_name = 'file.csv'
    content_type = Table.ContentType.CSV.value
    content = table_csv_content
    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content
    api_mock.call.return_value.json.return_value = reload_data_response

    result = table.get_content(content_type=content_type)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', table.eid, 'export'),
        params={
            'format': None,
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type


def test_get_content_json(api_mock, table_factory, reload_data_response):
    table = table_factory(name='file')
    file_name = 'file.json'
    content_type = Table.ContentType.JSON.value
    api_mock.call.return_value.json.return_value = reload_data_response

    result = table.get_content(content_type=content_type)

    rows = []
    for item in table:
        row = {}
        for cell in item:
            row[cell.name] = cell.content.dict()
        rows.append(row)

    api_mock.call.assert_called_with(
        method='GET',
        path=('adt', table.eid),
        params={
            'value': 'normalized',
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content_type == content_type
    assert result.content == json.dumps({'data': rows}, default=str).encode('utf-8')


def test_dump(table_factory, mocker, api_mock, reload_data_response, column_definitions_response, get_response_object):
    table = table_factory(name='name')
    file_name = 'name.json'
    content_type = 'application/json'

    api_mock.call.side_effect = [
        get_response_object(reload_data_response),
        get_response_object(column_definitions_response),
    ]

    fs_handler_mock = mocker.MagicMock()
    base_path = './'
    metadata = {
        'file_name': file_name,
        'content_type': content_type,
        'columns': ['Column 1', 'Column 2'],
        **{k: v for k, v in table.dict().items() if k in ('name', 'description', 'eid')},
    }
    table.dump(base_path=base_path, fs_handler=fs_handler_mock)

    rows = []
    for item in table:
        row = {}
        for cell in item:
            row[cell.name] = cell.content.dict()
        rows.append(row)
    content = json.dumps({'data': rows}, default=str).encode('utf-8')

    join_path_call_1 = mocker.call(base_path, table.eid, 'metadata.json')
    join_path_call_2 = mocker.call(base_path, table.eid, file_name)

    fs_handler_mock.join_path.assert_has_calls(
        [
            join_path_call_1,
            join_path_call_2,
        ],
        any_order=True,
    )
    fs_handler_mock.write.assert_has_calls(
        [
            mocker.call(fs_handler_mock.join_path(), json.dumps(metadata, default=str)),
            mocker.call(fs_handler_mock.join_path(), content),
        ],
        any_order=True,
    )


def test_load_table(
    api_mock,
    experiment_factory,
    eid_factory,
    mocker,
    table_json_content,
    get_response_object,
    templates,
    column_definitions_response,
    table_response,
    properties,
    reload_data_response,
    reload_data_response_square_table,
):
    container = experiment_factory()
    eid = eid_factory(type=EntityType.GRID)
    file_name = 'name.json'

    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'attributes': {
                'eid': eid,
                'name': file_name,
                'description': '',
                'type': EntityType.GRID,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '222',
            },
        },
    }
    fs_handler_mock = mocker.MagicMock()
    base_path = './'
    metadata = {
        'file_name': file_name,
        'name': file_name,
        'columns': ['Column 1', 'Column 2'],
    }
    response1 = table_response('table name')
    response2 = column_definitions_response
    response3 = properties
    response4 = reload_data_response

    api_mock.call.side_effect = [
        get_response_object(templates),
        get_response_object(column_definitions_response),
        get_response_object(response1),
        get_response_object(response2),
        get_response_object(response3),
        get_response_object(response3),
        get_response_object(reload_data_response_square_table),
        get_response_object(response4),
        get_response_object(response),
    ]

    fs_handler_mock.read.side_effect = [json.dumps(metadata), table_json_content]
    fs_handler_mock.join_path.side_effect = [base_path + 'metadata.json', base_path + file_name]

    Table.load(path=base_path, fs_handler=fs_handler_mock, parent=container)

    fs_handler_mock.join_path.assert_has_calls(
        [
            mocker.call(base_path, 'metadata.json'),
            mocker.call(base_path, file_name),
        ],
        any_order=True,
    )

    fs_handler_mock.read.assert_has_calls(
        [
            mocker.call(base_path + 'metadata.json'),
            mocker.call(base_path + file_name),
        ],
        any_order=True,
    )

    request = {
        'data': {
            'type': EntityType.GRID,
            'attributes': {'name': 'name.json'},
            'relationships': {
                'ancestors': {'data': [{'type': EntityType.EXPERIMENT, 'id': container.eid}]},
                'template': {'data': {'type': EntityType.GRID, 'id': 'grid:58726e57-a998-46f5-8b9e-b4760210ce74'}},
            },
        }
    }
    api_mock.call.assert_any_call(
        method='POST',
        path=('entities',),
        params={
            'digest': None,
            'force': 'true',
        },
        json=request,
    )


@pytest.mark.parametrize(
    'file_name, content_type',
    [
        ('name.csv', Table.ContentType.CSV),
        ('name.json', Table.ContentType.JSON),
    ],
)
def test_load_file(
    api_mock,
    experiment_factory,
    eid_factory,
    mocker,
    table_json_content,
    table_csv_content,
    get_response_object,
    templates,
    column_definitions_response,
    file_name,
    content_type,
):
    container = experiment_factory()
    eid = eid_factory(type=EntityType.GRID)

    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'attributes': {
                'eid': eid,
                'name': file_name,
                'description': '',
                'type': EntityType.GRID,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '222',
            },
        },
    }
    fs_handler_mock = mocker.MagicMock()
    base_path = './'
    metadata = {
        'file_name': file_name,
        'name': file_name,
        'columns': ['Column 1', 'Column 2', 'Column 3'],
        'content_type': content_type.value,
    }
    content = table_json_content if content_type == Table.ContentType.JSON else table_csv_content

    api_mock.call.side_effect = [
        get_response_object(templates),
        get_response_object(column_definitions_response),
        get_response_object(column_definitions_response),
        get_response_object(column_definitions_response),
        get_response_object(column_definitions_response),
        get_response_object(response),
    ]

    fs_handler_mock.read.side_effect = [json.dumps(metadata), content]
    fs_handler_mock.join_path.side_effect = [base_path + 'metadata.json', base_path + file_name]

    Table.load(path=base_path, fs_handler=fs_handler_mock, parent=container)

    fs_handler_mock.join_path.assert_has_calls(
        [
            mocker.call(base_path, 'metadata.json'),
            mocker.call(base_path, file_name),
        ],
        any_order=True,
    )

    fs_handler_mock.read.assert_has_calls(
        [
            mocker.call(base_path + 'metadata.json'),
            mocker.call(base_path + file_name),
        ],
        any_order=True,
    )

    api_mock.call.assert_any_call(
        method='POST',
        path=('entities', container.eid, 'children', file_name),
        params={
            'digest': None,
            'force': 'true',
        },
        headers={
            'Content-Type': content_type,
        },
        data=content,
    )
