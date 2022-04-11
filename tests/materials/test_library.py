import arrow

from signals_notebook.common_types import MaterialType, ObjectType
from signals_notebook.materials import Asset, Batch, Library


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
        assert item.created_at == arrow.get(raw_item['attributes']['created']['at'])
        assert item.edited_at == arrow.get(raw_item['attributes']['edited']['at'])


def test_get_asset(api_mock, mid_factory, library_factory):
    asset_name = 'AST-0001'
    library = library_factory()

    eid = mid_factory(type=MaterialType.ASSET)

    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.MATERIAL,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'assetTypeId': library.asset_type_id,
                'library': library.name,
                'eid': eid,
                'name': asset_name,
                'type': MaterialType.ASSET,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '1234234',
            },
        },
    }

    api_mock.call.return_value.json.return_value = response

    result = library.get_asset(asset_name)

    api_mock.call.assert_called_once_with(method='GET', path=('materials', library.name, 'assets', 'id', asset_name))

    assert isinstance(result, Asset)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_get_batch(api_mock, mid_factory, library_factory):
    batch_name = 'AST-0001-001'
    library = library_factory()

    eid = mid_factory(type=MaterialType.BATCH)

    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.MATERIAL,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'assetTypeId': library.asset_type_id,
                'library': library.name,
                'eid': eid,
                'name': batch_name,
                'type': MaterialType.BATCH,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '1234234',
            },
        },
    }

    api_mock.call.return_value.json.return_value = response

    result = library.get_batch(batch_name)

    api_mock.call.assert_called_once_with(method='GET', path=('materials', library.name, 'batches', 'id', batch_name))

    assert isinstance(result, Batch)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_get_asset_batches(api_mock, mid_factory, library_factory):
    asset_name = 'AST-0001'
    library = library_factory()

    eid1 = mid_factory(type=MaterialType.BATCH)
    eid2 = mid_factory(type=MaterialType.BATCH)

    response = {
        'links': {
            'self': (
                f'https://example.com/api/rest/v1.0/materials/{library.name}'
                '/assets/{asset_name}/batches?page[offset]=0&page[limit]=20'
            ),
            'first': (
                f'https://example.com/api/rest/v1.0/materials/{library.name}'
                '/assets/{asset_name}/batches?page[offset]=0&page[limit]=20'
            ),
        },
        'data': [
            {
                'type': ObjectType.MATERIAL,
                'id': eid1,
                'links': {'self': f'https://example.com/{eid1}'},
                'attributes': {
                    'assetTypeId': library.asset_type_id,
                    'library': library.name,
                    'eid': eid1,
                    'name': 'AST-0001-001',
                    'type': MaterialType.BATCH,
                    'createdAt': '2019-09-06T03:12:35.129Z',
                    'editedAt': '2019-09-06T15:22:47.309Z',
                    'digest': '1234234',
                },
            },
            {
                'type': ObjectType.MATERIAL,
                'id': eid2,
                'links': {'self': f'https://example.com/{eid2}'},
                'attributes': {
                    'assetTypeId': library.asset_type_id,
                    'library': library.name,
                    'eid': eid2,
                    'name': 'AST-0001-002',
                    'type': MaterialType.BATCH,
                    'createdAt': '2021-09-06T03:12:35.129Z',
                    'editedAt': '2021-09-06T15:22:47.309Z',
                    'digest': '1234233',
                },
            },
        ],
    }

    api_mock.call.return_value.json.return_value = response

    result = library.get_asset_batches(asset_name)

    api_mock.call.assert_called_once_with(
        method='GET', path=('materials', library.name, 'assets', asset_name, 'batches')
    )

    for item, raw_item, eid in zip(result, response['data'], [eid1, eid2]):
        assert isinstance(item, Batch)
        assert item.eid == eid
        assert item.digest == raw_item['attributes']['digest']
        assert item.name == raw_item['attributes']['name']
        assert item.created_at == arrow.get(raw_item['attributes']['createdAt'])
        assert item.edited_at == arrow.get(raw_item['attributes']['editedAt'])
