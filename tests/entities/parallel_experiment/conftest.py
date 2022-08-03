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
