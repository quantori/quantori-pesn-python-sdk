import pytest


@pytest.fixture()
def samples_from_table_response():
    return {
        'data': [
            {
                'type': 'samplesTableRow',
                'id': 'sample:0f96db87-a4af-46ae-9aff-711867f23d73',
                'attributes': {
                    'eid': 'sample:0f96db87-a4af-46ae-9aff-711867f23d73',
                    'columns': {
                        'subExpName': {
                            'key': 'subExpName',
                            'type': 'LINK',
                            'name': 'Name',
                            'content': {
                                'type': 'parasubexp',
                                'display': 'Sub-experiment-1',
                                'value': 'parasubexp:413779cf-16b9-49ce-bb85-85b2fa6964da',
                            },
                        },
                        'sampleId': {
                            'key': 'sampleId',
                            'type': 'LINK',
                            'name': 'ID',
                            'content': {
                                'type': 'sample',
                                'display': 'Sample-1764',
                                'value': 'sample:0f96db87-a4af-46ae-9aff-711867f23d73',
                            },
                        },
                        '1': {
                            'key': '1',
                            'type': 'DATETIME',
                            'name': 'Created Date',
                            'content': {'value': '2022-06-06T08:54:51.677884071Z'},
                        },
                        '2': {'key': '2', 'type': 'TEXT', 'name': 'Description', 'content': {'value': 'Description 1'}},
                        '3': {'key': '3', 'type': 'TEXT', 'name': 'Comments', 'content': {'value': 'Comments 1'}},
                        '4': {
                            'key': '4',
                            'type': 'UNIT',
                            'name': 'Amount',
                            'content': {'display': '1 g', 'value': 1.0, 'units': 'g'},
                        },
                        '10': {
                            'key': '10',
                            'type': 'CHILD_ENTITY_COUNT',
                            'name': 'Attached Docs',
                            'content': {'value': '0', 'eid': 'sample:0f96db87-a4af-46ae-9aff-711867f23d73'},
                        },
                        'sourceName': {
                            'key': 'sourceName',
                            'type': 'TEXT',
                            'name': 'Template',
                            'content': {'value': 'Sample'},
                        },
                    },
                },
            }
        ],
    }
