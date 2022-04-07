"""
This file contains common tests for all entity types.
"""

import arrow
import pytest

from signals_notebook.common_types import EID, EntityType, ObjectType
from signals_notebook.entities.notebook import Notebook


def test_get_list(api_mock):
    eid1 = EID('journal:878a87ca-3777-4692-8561-a4a81ccfd85d')
    eid2 = EID('journal:52062e1d-7e03-464f-8caf-d7ed93261213')
    response = {
        'links': {'self': f'https://example.com/{eid1}'},
        'data': [
            {
                'type': ObjectType.ENTITY,
                'id': eid1,
                'links': {'self': f'https://example.com/{eid1}'},
                'attributes': {
                    'eid': eid1,
                    'name': 'My notebook 1',
                    'description': 'test description 1',
                    'type': EntityType.NOTEBOOK,
                    'createdAt': '2020-09-06T03:12:35.129Z',
                    'editedAt': '2020-09-06T15:22:47.309Z',
                    'digest': '53263456',
                },
            },
            {
                'type': ObjectType.ENTITY,
                'id': eid2,
                'links': {'self': f'https://example.com/{eid2}'},
                'attributes': {
                    'eid': eid2,
                    'name': 'My notebook 2',
                    'description': 'test description 2',
                    'type': EntityType.NOTEBOOK,
                    'createdAt': '2021-09-06T03:12:35.129Z',
                    'editedAt': '2021-09-06T15:22:47.309Z',
                    'digest': '34563546',
                },
            },
        ],
    }
    api_mock.call.return_value.json.return_value = response

    result_generator = Notebook.get_list()

    api_mock.call.assert_not_called()

    result = list(result_generator)

    api_mock.call.assert_called_once_with(
        method='GET', path=('entities',), params={'includeTypes': EntityType.NOTEBOOK}
    )

    for item, raw_item in zip(result, response['data']):
        assert isinstance(item, Notebook)
        assert item.eid == raw_item['id']
        assert item.digest == raw_item['attributes']['digest']
        assert item.name == raw_item['attributes']['name']
        assert item.description == raw_item['attributes']['description']
        assert item.created_at == arrow.get(raw_item['attributes']['createdAt'])
        assert item.edited_at == arrow.get(raw_item['attributes']['editedAt'])


def test_delete(notebook_factory, api_mock):
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


def test_refresh(notebook_factory, entity_store_mock):
    notebook = notebook_factory(name='My notebook')

    notebook.refresh()

    entity_store_mock.refresh.assert_called_once_with(notebook)
