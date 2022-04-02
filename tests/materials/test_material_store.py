import arrow
import pytest

from signals_notebook.materials import Asset, Batch, Library, MaterialStore
from signals_notebook.types import MaterialType, ObjectType


@pytest.mark.parametrize(
    'material_type,expected_class',
    [
        (MaterialType.LIBRARY, Library),
        (MaterialType.ASSET, Asset),
        (MaterialType.BATCH, Batch),
    ],
)
def test_get(api_mock, mid_factory, material_type, expected_class):
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
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = MaterialStore.get(eid)

    api_mock.call.assert_called_once_with(method='GET', path=('materials', eid))

    assert isinstance(result, expected_class)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.description == response['data']['attributes']['description']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])
