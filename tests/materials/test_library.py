import arrow

from signals_notebook.materials import Library
from signals_notebook.types import MaterialType, ObjectType


def test_get_list_without_params(api_mock, mid_factory):
    eid1 = mid_factory(type=MaterialType.LIBRARY)
    eid2 = mid_factory(type=MaterialType.LIBRARY)
    response = {
        'data': [
            {
                'type': ObjectType.ASSET_TYPE,
                'id': eid1.id,
                'attributes': {
                    'name': 'Reagents (SNB)',
                    'id': eid1.id,
                    'enabled': True,
                    'assets': {},
                    'batches': {},
                    'displayImage': {'enabled': True, 'userChosen': False, 'useFieldId': '6172be4052faff000750114b'},
                    'created': {
                        'by': {
                            'links': {'self': 'https://example.com/api/rest/v1.0/users/3'},
                            'data': {'type': 'user', 'id': '3'},
                        },
                        'at': '2021-10-22T13:36:00.410080158Z',
                    },
                    'edited': {
                        'by': {
                            'links': {'self': 'https://example.com/api/rest/v1.0/users/3'},
                            'data': {'type': 'user', 'id': '3'},
                        },
                        'at': '2022-03-05T10:23:04.496761007Z',
                    },
                    'digest': '72475364:20620542',
                    'displayTable': {'content': ''},
                    'entityFlags': {
                        'isSystem': False,
                        'canTrash': True,
                        'canEditName': True,
                        'isTemplate': False,
                        'canEdit': True,
                        'canWrite': True,
                        'canComment': True,
                        'isShared': True,
                    },
                },
            },
            {
                'type': ObjectType.ASSET_TYPE,
                'id': eid2.id,
                'attributes': {
                    'name': 'Cell Lines',
                    'id': eid2.id,
                    'enabled': True,
                    'assets': {},
                    'batches': {},
                    'displayImage': {'enabled': True, 'userChosen': True, 'useFieldId': '6172be4052faff000750114e'},
                    'created': {
                        'by': {
                            'links': {'self': 'https://example.com/api/rest/v1.0/users/3'},
                            'data': {'type': 'user', 'id': '3'},
                        },
                        'at': '2021-10-22T13:36:00.414158292Z',
                    },
                    'edited': {
                        'by': {
                            'links': {'self': 'https://example.com/api/rest/v1.0/users/120'},
                            'data': {'type': 'user', 'id': '120'},
                        },
                        'at': '2022-02-04T12:27:58.888142151Z',
                    },
                    'digest': '33440458:55422053',
                    'displayTable': {'content': ''},
                    'materialsSampleMapping': {
                        'mapping': '',
                        'isEnabled': True,
                    },
                    'entityFlags': {
                        'isSystem': False,
                        'canTrash': True,
                        'canEditName': True,
                        'isTemplate': False,
                        'canEdit': True,
                        'canWrite': True,
                        'canComment': True,
                        'isShared': True,
                    },
                },
            },
        ]
    }
    api_mock.call.return_value.json.return_value = response

    result = Library.get_list()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('materials', 'libraries'),
    )

    for item, raw_item in zip(result, response['data']):
        assert isinstance(item, Library)
        assert item.eid == f'{MaterialType.LIBRARY}:{raw_item["id"]}'
        assert item.digest == raw_item['attributes']['digest'].split(':')[0]
        assert item.name == raw_item['attributes']['name']
        assert item.description is None
        assert item.created_at == arrow.get(raw_item['attributes']['created']['at'])
        assert item.edited_at == arrow.get(raw_item['attributes']['edited']['at'])
