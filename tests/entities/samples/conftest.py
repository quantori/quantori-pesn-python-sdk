import pytest


@pytest.fixture()
def sample_properties():
    return {
        'links': {'self': 'https://example.com/samples/properties'},
        'data': [
            {
                'type': 'property',
                'id': 'b718adec-73e0-3ce3-ac72-0dd11a06a308',
                'attributes': {
                    'id': 'b718adec-73e0-3ce3-ac72-0dd11a06a308',
                    'name': 'ID',
                    'content': {'value': 'Sample-1756'},
                },
            },
            {
                'type': 'property',
                'id': '278c491b-dd8a-3361-8c14-9c4ac790da34',
                'attributes': {
                    'id': '278c491b-dd8a-3361-8c14-9c4ac790da34',
                    'name': 'Template',
                    'content': {'value': 'Sample'},
                },
            },
            {
                'type': 'property',
                'id': 'digests.self',
                'attributes': {'id': 'digests.self'},
            },
            {
                'type': 'property',
                'id': 'digests.external',
                'attributes': {'id': 'digests.external'},
            },
            {
                'type': 'property',
                'id': '1',
                'attributes': {
                    'id': '1',
                    'name': 'Created Date',
                    'content': {'value': '2022-06-02T07:27:10.072365283Z'},
                },
            },
            {
                'type': 'property',
                'id': '2',
                'attributes': {'id': '2', 'name': 'Description', 'content': {'value': 'simple'}},
            },
            {
                'type': 'property',
                'id': '3',
                'attributes': {'id': '3', 'name': 'Comments', 'content': {'value': '555'}},
            },
        ],
    }


@pytest.fixture()
def templates():
    return {
        'links': {
            'self': 'https://ex.com/api/rest/v1.0/'
            'entities?includeTypes=sample&includeOptions=template&page[offset]=0&page[limit]=20',
            'first': 'https://ex.com/api/rest/v1.0/'
            'entities?includeTypes=sample&includeOptions=template&page[offset]=0&page[limit]=20',
        },
        'data': [
            {
                'type': 'entity',
                'id': 'sample:fcaa5e11-ace8-4d2c-a212-293dad3c2122',
                'links': {'self': 'https://ex.com/api/rest/v1.0/entities/sample:fcaa5e11-ace8-4d2c-a212-293dad3c2122'},
                'attributes': {
                    'id': 'sample:fcaa5e11-ace8-4d2c-a212-293dad3c2122',
                    'eid': 'sample:fcaa5e11-ace8-4d2c-a212-293dad3c2122',
                    'name': 'Sample',
                    'description': '',
                    'createdAt': '2021-10-22T13:36:03.908Z',
                    'editedAt': '2021-11-11T10:46:49.703Z',
                    'type': 'sample',
                    'digest': '68360779',
                    'fields': {'Description': {'value': ''}, 'Name': {'value': 'Sample'}},
                    'flags': {'canEdit': True},
                },
            },
        ],
    }
