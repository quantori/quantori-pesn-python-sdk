import arrow
import pytest

from signals_notebook.common_types import MaterialType, ObjectType
from signals_notebook.materials import Asset, Batch, Library, MaterialStore


@pytest.mark.parametrize(
    'material_type,expected_class',
    [
        (MaterialType.ASSET, Asset),
        (MaterialType.BATCH, Batch),
    ],
)
def test_get(api_mock, mid_factory, material_type, expected_class, library_factory, mocker):
    library = library_factory()
    mocker.patch.object(Asset, 'library', new=property(lambda x: library))
    mocker.patch.object(Batch, 'library', new=property(lambda x: library))

    eid = mid_factory(type=material_type)

    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.MATERIAL,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'assetTypeId': eid.id,
                'library': 'Plasmids',
                'eid': eid,
                'name': 'Plasmids',
                'description': 'test description',
                'type': material_type,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '1234234',
                'fields': {
                    'Name': {
                        'value': 'test',
                    },
                },
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = MaterialStore.get(eid)

    api_mock.call.assert_called_once_with(method='GET', path=('materials', eid))

    assert isinstance(result, expected_class)
    assert str(result) == f'<{expected_class.__name__} eid={result.eid}>'

    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])
    assert result['Name'] == 'test'


def test_get_library(api_mock, mid_factory):
    eid = mid_factory(type=MaterialType.LIBRARY)

    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.MATERIAL,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'assetTypeId': eid.id,
                'library': 'Plasmids',
                'eid': eid,
                'name': 'Plasmids',
                'description': 'test description',
                'type': MaterialType.LIBRARY,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '1234234',
                'fields': {
                    'String field': {
                        'value': 'test',
                    },
                    'String list field': {
                        'value': [
                            'test1',
                            'test2',
                        ]
                    },
                },
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = MaterialStore.get(eid)

    api_mock.call.assert_called_once_with(method='GET', path=('materials', eid))

    assert isinstance(result, Library)
    assert str(result) == f'<{Library.__name__} eid={result.eid}>'

    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])
