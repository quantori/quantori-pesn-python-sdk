from signals_notebook.entities.tables.cell import ColumnDefinition
from signals_notebook.entities.tables.row import Row
from signals_notebook.types import EntityType, ObjectType


def test_reload_data(api_mock, table_factory, eid_factory):
    eid = eid_factory(type=EntityType.GRID)
    table = table_factory(eid=eid)
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': [
            {
                'type': ObjectType.ADT_ROW,
                'id': '885f33fb-73bd-49a3-a394-2d21ea9d3c71',
                'attributes': {'id': '885f33fb-73bd-49a3-a394-2d21ea9d3c71', 'type': ObjectType.ADT_ROW, 'cells': []},
            },
            {
                'type': ObjectType.ADT_ROW,
                'id': '60ce72ef-2770-4e55-bcb3-f63beb9024b2',
                'attributes': {'id': '60ce72ef-2770-4e55-bcb3-f63beb9024b2', 'type': ObjectType.ADT_ROW, 'cells': []},
            },
        ],
    }
    api_mock.call.return_value.json.return_value = response

    table._reload_data()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('adt', eid),
        params={
            'value': 'normalized',
        },
    )

    assert len(table._rows) == 2
    assert len(table._rows_by_id) == 2

    for i in range(2):
        assert isinstance(table._rows[i], Row)


def test_get_column_definitions_list(api_mock, table_factory, eid_factory):
    eid = eid_factory(type=EntityType.GRID)
    table = table_factory(eid=eid)
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.COLUMN_DEFINITIONS,
            'id': eid,
            'attributes': {
                'id': eid,
                'type': ObjectType.COLUMN_DEFINITIONS,
                'columns': [
                    {'key': 'fac1b3c0-c262-4b47-92c2-5f6535536ca3', 'title': 'Column 1', 'type': 'text', 'saved': True},
                    {'key': '15c9d0ef-3873-481f-bb1b-5d719bde0598', 'title': 'Column 2', 'type': 'text', 'saved': True},
                ],
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = table.get_column_definitions_list()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('adt', eid, '_column'),
    )

    assert len(result) == 2

    for i in range(2):
        assert isinstance(result[i], ColumnDefinition)
        assert str(result[i].key) == response['data']['attributes']['columns'][i]['key']
        assert result[i].title == response['data']['attributes']['columns'][i]['title']
        assert result[i].type == response['data']['attributes']['columns'][i]['type']
        assert result[i].saved == response['data']['attributes']['columns'][i]['saved']
