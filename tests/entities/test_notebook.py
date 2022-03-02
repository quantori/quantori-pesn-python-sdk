import arrow
import pytest

from signals_notebook.entities.notebook import Notebook
from signals_notebook.types import EID, EntitySubtype, EntityType


def test_get_list(api_mock):
    eid1 = EID('journal:878a87ca-3777-4692-8561-a4a81ccfd85d')
    eid2 = EID('journal:52062e1d-7e03-464f-8caf-d7ed93261213')
    response = {
        'links': {'self': f'https://example.com/{eid1}'},
        'data': [
            {
                'type': EntityType.ENTITY,
                'id': eid1,
                'links': {'self': f'https://example.com/{eid1}'},
                'attributes': {
                    'eid': eid1,
                    'name': 'My notebook 1',
                    'description': 'test description 1',
                    'type': EntitySubtype.NOTEBOOK,
                    'createdAt': '2020-09-06T03:12:35.129Z',
                    'editedAt': '2020-09-06T15:22:47.309Z',
                    'digest': '53263456',
                },
            },
            {
                'type': EntityType.ENTITY,
                'id': eid2,
                'links': {'self': f'https://example.com/{eid2}'},
                'attributes': {
                    'eid': eid2,
                    'name': 'My notebook 2',
                    'description': 'test description 2',
                    'type': EntitySubtype.NOTEBOOK,
                    'createdAt': '2021-09-06T03:12:35.129Z',
                    'editedAt': '2021-09-06T15:22:47.309Z',
                    'digest': '34563546',
                },
            },
        ],
    }
    api_mock.call.return_value.json.return_value = response

    result = Notebook.get_list()

    api_mock.call.assert_called_once_with(
        method='GET', path=('entities',), params={'includeTypes': EntitySubtype.NOTEBOOK}
    )

    for item, raw_item in zip(result, response['data']):
        assert isinstance(item, Notebook)
        assert item.eid == raw_item['id']
        assert item.digest == raw_item['attributes']['digest']
        assert item.name == raw_item['attributes']['name']
        assert item.description == raw_item['attributes']['description']
        assert item.created_at == arrow.get(raw_item['attributes']['createdAt'])
        assert item.edited_at == arrow.get(raw_item['attributes']['editedAt'])


@pytest.mark.parametrize('description', ['test description', None])
@pytest.mark.parametrize('digest, force', [('1234234', False), (None, True)])
def test_create(api_mock, description, digest, force):
    eid = EID('journal:e360eea6-b331-4c6f-b340-6d0eaa7eb070')
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': EntityType.ENTITY,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'eid': eid,
                'name': 'My notebook',
                'description': description,
                'type': EntitySubtype.NOTEBOOK,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': digest,
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = Notebook.create(name='My notebook', description=description, digest=digest, force=force)

    request_body = {
        'data': {
            'type': EntitySubtype.NOTEBOOK,
            'attributes': {
                'name': response['data']['attributes']['name'],
            },
        }
    }

    if description:
        request_body['data']['attributes']['description'] = description

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('entities',),
        params={
            'digest': digest,
            'force': 'true' if force else 'false',
        },
        json=request_body,
    )

    assert isinstance(result, Notebook)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.description == response['data']['attributes']['description']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_delete_instance(notebook_factory, api_mock):
    notebook = notebook_factory()

    notebook.delete()

    api_mock.call.assert_called_once_with(
        method='DELETE',
        path=('entities', notebook.eid),
        params={
            'digest': None,
            'force': 'true',
        },
    )


@pytest.mark.parametrize('force', [True, False])
def test_update(api_mock, notebook_factory, force):
    notebook = notebook_factory()

    notebook.name = 'My notebook'
    notebook.description = 'New description'
    notebook.save(force=force)

    api_mock.call.assert_called_once_with(
        method='PATCH',
        path=('entities', notebook.eid, 'properties'),
        params={
            'digest': None if force else notebook.digest,
            'force': 'true' if force else 'false',
        },
        json={
            'data': [
                {'attributes': {'name': 'Name', 'value': 'My notebook'}},
                {'attributes': {'name': 'Description', 'value': 'New description'}},
            ]
        },
    )
