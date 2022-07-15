import arrow
import pytest

from signals_notebook.common_types import File, MaterialType, ObjectType
from signals_notebook.materials import Asset, Batch, Library
from signals_notebook.materials.library import (
    AssetRelationship,
    AssetRequestData,
    BatchAssetAttribute,
    BatchRequestData,
    DataRelationship,
)
from tests.entities.factories import TextFactory


def test_get_list(api_mock, mid_factory):
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
                    'assets': {
                        'assetNameFieldId': '6172be4052faff000750114c',
                        'displayName': 'Reagent',
                        'numbering': {'format': 'RGT-{####}'},
                        'fields': [
                            {
                                'id': '6172be4052faff000750114c',
                                'name': 'Chemical Name',
                                'dataType': 'TEXT',
                                'mandatory': True,
                                'hidden': False,
                                'definedBy': 'SYSTEM_DEFAULT',
                            },
                            {
                                'id': '6172be4052faff000750114b',
                                'name': 'Chemical Structure',
                                'dataType': 'CHEMICAL_DRAWING',
                                'mandatory': False,
                                'hidden': True,
                                'definedBy': 'SYSTEM_DEFAULT',
                            },
                        ],
                    },
                    'batches': {
                        'displayName': 'Lot',
                        'fields': [
                            {
                                'id': '6172be4052faff000750116d',
                                'name': '% active',
                                'dataType': 'PERCENTAGE',
                                'mandatory': False,
                                'hidden': False,
                                'definedBy': 'SYSTEM_DEFAULT',
                            },
                            {
                                'id': '6172be4052faff000750116e',
                                'name': 'Amount',
                                'dataType': 'MASS',
                                'mandatory': True,
                                'hidden': False,
                                'definedBy': 'SYSTEM_DEFAULT',
                            },
                        ],
                        'numbering': {'format': '{####}'},
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
                    'assets': {
                        'assetNameFieldId': '6172be4052faff000750114d',
                        'displayName': 'Cell Line',
                        'numbering': {'format': 'PKI-{######}'},
                        'fields': [
                            {
                                'id': '6172be4052faff000750114d',
                                'name': 'Cell Line Name',
                                'dataType': 'TEXT',
                                'mandatory': True,
                                'hidden': False,
                                'definedBy': 'SYSTEM_DEFAULT',
                            },
                            {
                                'id': '6172be4052faff000750119d',
                                'name': 'Organism',
                                'dataType': 'TEXT',
                                'mandatory': True,
                                'hidden': False,
                                'definedBy': 'SYSTEM_DEFAULT',
                                'options': [
                                    'Bovine',
                                    'Dog',
                                    'Hamster',
                                    'Human',
                                    'Monkey',
                                    'Mouse',
                                    'Pig',
                                    'Rat',
                                    'Rhesus Monkey',
                                    'Sheep',
                                    'E. coli',
                                ],
                                'collection': 'LIST',
                            },
                        ],
                    },
                    'batches': {
                        'displayName': 'Lot',
                        'fields': [
                            {
                                'id': '6172be4052faff00075011a6',
                                'name': 'Passage #',
                                'dataType': 'INTEGER',
                                'mandatory': False,
                                'hidden': False,
                                'definedBy': 'SYSTEM_DEFAULT',
                            },
                            {
                                'id': '6172be4052faff00075011a7',
                                'name': 'Cell Count',
                                'dataType': 'DECIMAL',
                                'mandatory': False,
                                'hidden': False,
                                'definedBy': 'SYSTEM_DEFAULT',
                            },
                        ],
                        'numbering': {'format': '{####}'},
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


def test_create_batch(api_mock, mid_factory, library_factory):
    asset_name = 'AST-0001'
    batch_name = 'BTCH-0001'

    library = library_factory()

    batch_eid = mid_factory(type=MaterialType.BATCH)
    asset_eid = mid_factory(type=MaterialType.ASSET)
    response = {
        'links': {'self': f'https://example.com/api/rest/v1.0/materials/batch:{batch_eid}'},
        'data': {
            'type': 'material',
            'id': f'batch:{batch_eid.id}',
            'links': {'self': f'https://example.com/api/rest/v1.0/materials/batch:{batch_eid}'},
            'attributes': {
                'library': library.name,
                'assetTypeId': library.asset_type_id,
                'assetId': asset_eid.id,
                'id': f'batch:{batch_eid.id}',
                'eid': f'batch:{batch_eid.id}',
                'name': batch_name,
                'description': '',
                'createdAt': '2022-05-25T07:45:39.294Z',
                'editedAt': '2022-05-25T07:45:39.294Z',
                'type': 'batch',
                'digest': '64701446',
            },
        },
    }

    api_mock.call.return_value.json.return_value = response
    text = TextFactory()
    result = library.create_batch(asset_name=asset_name, batch_fields={'Link Name': text})

    request_data = BatchRequestData(
        type='batch',
        attributes=BatchAssetAttribute(
            fields=[
                {
                    'id': library.batch_config.fields[1].id,
                    'value': {
                        'eid': text.eid,
                        'name': text.name,
                        'type': text.type,
                    },
                }
            ]
        ),
    )

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('materials', library.name, 'assets', asset_name, 'batches'),
        json={'data': request_data.dict()},
    )

    assert isinstance(result, Batch)
    assert result.eid == batch_eid
    assert result.library_name == response['data']['attributes']['library']
    assert result.name == response['data']['attributes']['name']
    assert result.type == response['data']['attributes']['type']
    assert result.digest == response['data']['attributes']['digest']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_create_asset_with_batches(api_mock, mid_factory, library_factory):
    asset_name = 'AST-0001'

    library = library_factory()

    batch_eid = mid_factory(type=MaterialType.BATCH)
    asset_eid = mid_factory(type=MaterialType.ASSET)
    response = {
        'links': {'self': f'https://example.com/api/rest/v1.0/materials/asset:{asset_eid.id}'},
        'data': {
            'type': 'material',
            'id': f'asset:{asset_eid.id}',
            'links': {'self': f'https://example.com/api/rest/v1.0/materials/asset:{asset_eid.id}'},
            'attributes': {
                'library': library.name,
                'assetTypeId': library.asset_type_id,
                'assetId': asset_eid.id,
                'id': f'asset:{asset_eid.id}',
                'eid': f'asset:{asset_eid.id}',
                'name': asset_name,
                'description': '',
                'createdAt': '2022-05-25T07:45:39.294Z',
                'editedAt': '2022-05-25T07:45:39.294Z',
                'type': 'asset',
                'digest': '64701446',
            },
            'relationships': {
                'batches': {'data': [{'type': 'material', 'id': f'batch:{batch_eid.id}'}]},
            },
        },
    }

    api_mock.call.return_value.json.return_value = response
    text = TextFactory()
    result = library.create_asset_with_batches(
        asset_with_batch_fields={'asset': {'Name': 'Created'}, 'batch': {'Link Name': text}}
    )
    request_data = AssetRequestData(
        type='asset',
        attributes=BatchAssetAttribute(fields=[{'id': library.asset_config.fields[0].id, 'value': 'Created'}]),
        relationships=AssetRelationship(
            batch=DataRelationship(
                data=BatchRequestData(
                    type='batch',
                    attributes=BatchAssetAttribute(
                        fields=[
                            {
                                'id': library.batch_config.fields[1].id,
                                'value': {
                                    'eid': text.eid,
                                    'name': text.name,
                                    'type': text.type,
                                },
                            }
                        ]
                    ),
                )
            )
        ),
    )

    api_mock.call.assert_called_once_with(
        method='POST', path=('materials', library.name, 'assets'), json={'data': request_data.dict()}
    )

    assert isinstance(result, Asset)
    assert result.eid == asset_eid
    assert result.library_name == response['data']['attributes']['library']
    assert result.name == response['data']['attributes']['name']
    assert result.type == response['data']['attributes']['type']
    assert result.digest == response['data']['attributes']['digest']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


@pytest.fixture()
def get_response(mocker):
    def _f(response):
        mock = mocker.Mock()
        mock.status_code = 200
        mock.json.return_value = response
        return mock

    return _f


def test_get_content(library_factory, api_mock, mocker, get_response):
    library = library_factory()
    content = b'Content'
    content_type = 'text/csv'

    response1 = {
        'data': {
            'type': 'bulkExportReport',
            'id': '6beeaaa6-c6bb-4226-919d-f3ea8a9a2af9',
            'attributes': {'fileId': '6beeaaa6-c6bb-4226-919d-f3ea8a9a2af9', 'reportId': '62b58331d8bb040577c1850d'},
        }
    }

    response2 = {
        'data': {
            'type': 'materialBulkExportReport',
            'id': '62b58331d8bb040577c1850d',
            'attributes': {
                'id': '62b58331d8bb040577c1850d',
                'libraryName': library.name,
                'createdAt': '2022-06-24T09:26:09.723014517Z',
                'startedAt': '2022-06-24T09:26:09.724814132Z',
                'completedAt': '2022-06-24T09:26:10.786280759Z',
                'modifiedAtSecsSinceEpoch': 0,
                'status': 'COMPLETED',
                'fileId': '6beeaaa6-c6bb-4226-919d-f3ea8a9a2af9',
                'count': 5,
                'total': 5,
            },
        }
    }
    file_id, report_id = response1['data']['attributes'].values()

    content_response = get_response({})
    content_response.content = content
    content_response.headers = {
        'content-type': 'text/csv',
        'content-disposition': f'attachment; filename={library.name}',
    }

    api_mock.call.side_effect = [get_response(response1), get_response(response2), content_response]

    result = library.get_content()

    api_mock.call.assert_has_calls(
        [
            mocker.call(
                method='POST',
                path=('materials', library.name, 'bulkExport'),
            ),
            mocker.call(
                method='GET',
                path=('materials', 'bulkExport', 'reports', report_id),
            ),
            mocker.call(
                method='GET',
                path=('materials', 'bulkExport', 'download', file_id),
            ),
        ],
        any_order=False,
    )

    assert isinstance(result, File)
    assert result.name == library.name
    assert result.content == content
    assert result.content_type == content_type


def test_get_content_timeout(library_factory, api_mock, get_response):
    library = library_factory()
    content = b'Content'

    response1 = {
        'data': {
            'type': 'bulkExportReport',
            'id': '6beeaaa6-c6bb-4226-919d-f3ea8a9a2af9',
            'attributes': {'fileId': '6beeaaa6-c6bb-4226-919d-f3ea8a9a2af9', 'reportId': '62b58331d8bb040577c1850d'},
        }
    }

    response2 = {
        'data': {
            'type': 'materialBulkExportReport',
            'id': '62b58331d8bb040577c1850d',
            'attributes': {
                'id': '62b58331d8bb040577c1850d',
                'libraryName': library.name,
                'createdAt': '2022-06-24T09:26:09.723014517Z',
                'startedAt': '2022-06-24T09:26:09.724814132Z',
                'completedAt': '2022-06-24T09:26:10.786280759Z',
                'modifiedAtSecsSinceEpoch': 0,
                'status': 'FAILED',
                'fileId': '6beeaaa6-c6bb-4226-919d-f3ea8a9a2af9',
                'count': 5,
                'total': 5,
            },
        }
    }
    content_response = get_response({})
    content_response.content = content
    content_response.headers = {
        'content-type': 'text/csv',
        'content-disposition': f'attachment; filename={library.name}',
    }

    api_mock.call.side_effect = [get_response(response1), get_response(response2), content_response]

    with pytest.raises(TimeoutError) as e:
        library.get_content(timeout=1)

    assert str(e.value) == 'Time is over to get file'


def test_get_content_empty_library(library_factory, api_mock, get_response, mocker):
    library = library_factory()

    response1 = {
        'data': {
            'type': 'bulkExportReport',
            'id': '6beeaaa6-c6bb-4226-919d-f3ea8a9a2af9',
            'attributes': {'fileId': '6beeaaa6-c6bb-4226-919d-f3ea8a9a2af9', 'reportId': '62b58331d8bb040577c1850d'},
        }
    }

    response2 = {
        'data': {
            'type': 'materialBulkExportReport',
            'id': '62b58331d8bb040577c1850d',
            'attributes': {
                'id': '62b58331d8bb040577c1850d',
                'libraryName': library.name,
                'createdAt': '2022-06-24T09:26:09.723014517Z',
                'startedAt': '2022-06-24T09:26:09.724814132Z',
                'completedAt': '2022-06-24T09:26:10.786280759Z',
                'modifiedAtSecsSinceEpoch': 0,
                'status': 'FAILED',
                'fileId': '6beeaaa6-c6bb-4226-919d-f3ea8a9a2af9',
                'count': 5,
                'total': 5,
                "error": {
                    "description": "Nothing to export."
                }
            },
        }
    }
    file_id, report_id = response1['data']['attributes'].values()


    api_mock.call.side_effect = [get_response(response1), get_response(response2)]

    result = library.get_content()

    api_mock.call.assert_has_calls(
        [
            mocker.call(
                method='POST',
                path=('materials', library.name, 'bulkExport'),
            ),
            mocker.call(
                method='GET',
                path=('materials', 'bulkExport', 'reports', report_id),
            ),
        ],
        any_order=False,
    )

    assert isinstance(result, File)
    assert result.name == f'{library.name}_empty'
    assert result.content == b'The library is empty'
    assert result.content_type == 'text/csv'


@pytest.mark.parametrize(
    'rule',
    [
        'NO_DUPLICATED',
        'TREAT_AS_UNIQUE',
        'USE_MATCHES',
    ],
)
def test_bulk_import_json_format(library_factory, api_mock, mocker, get_response, rule):
    library = library_factory()
    text = TextFactory()
    import_type = 'json'

    response1 = {
        'data': {
            'type': 'assetBulkImportReport',
            'id': '62be94847f79d37108f6df6c',
            'attributes': {
                'id': '62be94847f79d37108f6df6c',
                'assetType': {
                    'id': '619656d40669900007d69414',
                    'name': library.name,
                    'type': 'CUSTOM',
                },
                'createdAt': '2022-07-01T06:30:28.33667103Z',
                'report': {
                    'filename': 'file-to-import.zip',
                    'succeeded': 0,
                    'duplicated': 0,
                    'failed': 0,
                },
                'status': 'IMPORTING',
                'rule': 'TREAT_AS_UNIQUE',
                'zoneId': 'Etc/UTC',
            },
        }
    }

    response2 = {
        'data': {
            'type': 'assetBulkImportReport',
            'id': '62be94847f79d37108f6df6c',
            'attributes': {
                'id': '62be94847f79d37108f6df6c',
                'assetType': {
                    'id': '619656d40669900007d69414',
                    'name': library.name,
                    'type': 'CUSTOM',
                },
                'createdAt': '2022-07-01T06:30:28.33667103Z',
                'startedAt': '2022-07-01T06:30:28.588380919Z',
                'completedAt': '2022-07-01T06:30:34.032774548Z',
                'report': {
                    'filename': 'file-to-import.zip',
                    'succeeded': 3,
                    'duplicated': 0,
                    'failed': 0,
                },
                'status': 'COMPLETED',
                'rule': rule,
                'zoneId': 'Etc/UTC',
            },
        }
    }
    request_data = AssetRequestData(
        type='asset',
        attributes=BatchAssetAttribute(fields=[{'id': library.asset_config.fields[0].id, 'value': 'Created'}]),
        relationships=AssetRelationship(
            batch=DataRelationship(
                data=BatchRequestData(
                    type='batch',
                    attributes=BatchAssetAttribute(
                        fields=[
                            {
                                'id': library.batch_config.fields[1].id,
                                'value': {
                                    'eid': text.eid,
                                    'name': text.name,
                                    'type': text.type,
                                },
                            }
                        ]
                    ),
                )
            )
        ),
    )
    job_id = response1['data']['id']

    api_mock.call.side_effect = [get_response(response1), get_response(response2)]

    library.bulk_import(
        materials=[{'asset': {'Name': 'Created'}, 'batch': {'Link Name': text}}],
        rule=rule,
        import_type=import_type,
    )

    api_mock.call.assert_has_calls(
        [
            mocker.call(
                method='POST',
                path=('materials', library.name, 'bulkImport'),
                params={
                    'rule': rule,
                    'importType': import_type,
                },
                json=[{'data': request_data.dict()}],
            ),
            mocker.call(
                method='GET',
                path=('materials', 'bulkImport', 'jobs', job_id),
            ),
        ],
        any_order=False,
    )


@pytest.mark.parametrize(
    'rule',
    [
        'NO_DUPLICATED',
        'TREAT_AS_UNIQUE',
        'USE_MATCHES',
    ],
)
def test_bulk_import_zip_format(library_factory, file_factory, api_mock, mocker, get_response, rule):
    content = b'content'
    content_type = 'application/octet-stream'

    file = file_factory(content=content, content_type=content_type)

    library = library_factory()
    import_type = 'zip'

    response1 = {
        'data': {
            'type': 'assetBulkImportReport',
            'id': '62be94847f79d37108f6df6c',
            'attributes': {
                'id': '62be94847f79d37108f6df6c',
                'assetType': {
                    'id': '619656d40669900007d69414',
                    'name': library.name,
                    'type': 'CUSTOM',
                },
                'createdAt': '2022-07-01T06:30:28.33667103Z',
                'report': {
                    'filename': 'file-to-import.zip',
                    'succeeded': 0,
                    'duplicated': 0,
                    'failed': 0,
                },
                'status': 'IMPORTING',
                'rule': 'TREAT_AS_UNIQUE',
                'zoneId': 'Etc/UTC',
            },
        }
    }

    response2 = {
        'data': {
            'type': 'assetBulkImportReport',
            'id': '62be94847f79d37108f6df6c',
            'attributes': {
                'id': '62be94847f79d37108f6df6c',
                'assetType': {
                    'id': '619656d40669900007d69414',
                    'name': library.name,
                    'type': 'CUSTOM',
                },
                'createdAt': '2022-07-01T06:30:28.33667103Z',
                'startedAt': '2022-07-01T06:30:28.588380919Z',
                'completedAt': '2022-07-01T06:30:34.032774548Z',
                'report': {
                    'filename': 'file-to-import.zip',
                    'succeeded': 3,
                    'duplicated': 0,
                    'failed': 0,
                },
                'status': 'COMPLETED',
                'rule': rule,
                'zoneId': 'Etc/UTC',
            },
        }
    }

    job_id = response1['data']['id']

    api_mock.call.side_effect = [get_response(response1), get_response(response2)]

    library.bulk_import(materials=file, rule=rule, import_type=import_type)

    api_mock.call.assert_has_calls(
        [
            mocker.call(
                method='POST',
                path=('materials', library.name, 'bulkImport'),
                params={
                    'rule': rule,
                    'importType': import_type,
                },
                headers={
                    'Content-Type': content_type,
                },
                data=file.content,
            ),
            mocker.call(
                method='GET',
                path=('materials', 'bulkImport', 'jobs', job_id),
            ),
        ],
        any_order=False,
    )


@pytest.mark.parametrize(
    'rule',
    [
        'NO_DUPLICATED',
        'TREAT_AS_UNIQUE',
        'USE_MATCHES',
    ],
)
def test_bulk_import_zip_format_timeout(library_factory, file_factory, api_mock, mocker, get_response, rule):
    content = b'content'
    content_type = 'application/octet-stream'

    file = file_factory(content=content, content_type=content_type)

    library = library_factory()
    import_type = 'zip'

    response1 = {
        'data': {
            'type': 'assetBulkImportReport',
            'id': '62be94847f79d37108f6df6c',
            'attributes': {
                'id': '62be94847f79d37108f6df6c',
                'assetType': {
                    'id': '619656d40669900007d69414',
                    'name': library.name,
                    'type': 'CUSTOM',
                },
                'createdAt': '2022-07-01T06:30:28.33667103Z',
                'report': {
                    'filename': 'file-to-import.zip',
                    'succeeded': 0,
                    'duplicated': 0,
                    'failed': 0,
                },
                'status': 'IMPORTING',
                'rule': 'TREAT_AS_UNIQUE',
                'zoneId': 'Etc/UTC',
            },
        }
    }

    response2 = {
        'data': {
            'type': 'assetBulkImportReport',
            'id': '62be94847f79d37108f6df6c',
            'attributes': {
                'id': '62be94847f79d37108f6df6c',
                'assetType': {
                    'id': '619656d40669900007d69414',
                    'name': library.name,
                    'type': 'CUSTOM',
                },
                'createdAt': '2022-07-01T06:30:28.33667103Z',
                'startedAt': '2022-07-01T06:30:28.588380919Z',
                'completedAt': '2022-07-01T06:30:34.032774548Z',
                'report': {
                    'filename': 'file-to-import.zip',
                    'succeeded': 3,
                    'duplicated': 0,
                    'failed': 0,
                },
                'status': 'FAILED',
                'rule': rule,
                'zoneId': 'Etc/UTC',
            },
        }
    }
    failure_response = get_response({})
    failure_response.content = content
    failure_response.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={library.name}_failure_report',
    }

    job_id = response1['data']['id']

    api_mock.call.side_effect = [get_response(response1), get_response(response2), failure_response]

    result = library.bulk_import(materials=file, rule=rule, import_type=import_type, timeout=1)

    api_mock.call.assert_has_calls(
        [
            mocker.call(
                method='POST',
                path=('materials', library.name, 'bulkImport'),
                params={
                    'rule': rule,
                    'importType': import_type,
                },
                headers={
                    'Content-Type': content_type,
                },
                data=file.content,
            ),
            mocker.call(
                method='GET',
                path=('materials', 'bulkImport', 'jobs', job_id),
            ),
            mocker.call(
                method='GET',
                path=('materials', 'bulkImport', 'jobs', job_id, 'failures'),
                params={
                    'filename': f'{library.name}_failure_report',
                },
            ),
        ],
        any_order=False,
    )

    assert isinstance(result, File)
    assert result.name == f'{library.name}_failure_report'
    assert result.content == content
    assert result.content_type == content_type
