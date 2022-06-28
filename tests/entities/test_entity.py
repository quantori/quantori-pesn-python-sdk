"""
This file contains common tests for all entity types.
"""
import datetime
from uuid import UUID

import arrow
import pytest

from signals_notebook.common_types import EID, EntityType, ObjectType
from signals_notebook.entities.entity import Property
from signals_notebook.entities.notebook import Notebook


@pytest.fixture()
def properties():
    return {
        "links": {
            "self": "https://example.com/api/rest/v1.0/entities/journal:111a8a0d-2772-47b0-b5b8-2e4faf04119e/properties"
        },
        "data": [
            {
                "type": "property",
                "id": "3103",
                "meta": {
                    "definition": {
                        "type": "text",
                        "attribute": {"id": "1", "name": "Text", "type": "text", "counts": {"templates": {}}},
                    }
                },
                "attributes": {
                    "id": "3103",
                    "name": "Name",
                    "value": "Test creation by SDK",
                    "values": ["Test creation by SDK"],
                },
            },
            {
                "type": "property",
                "id": "3102",
                "meta": {
                    "definition": {
                        "type": "text",
                        "attribute": {"id": "1", "name": "Text", "type": "text", "counts": {"templates": {}}},
                    }
                },
                "attributes": {
                    "id": "3102",
                    "name": "Description",
                    "value": "Created by Eugene Pokidov",
                    "values": ["Created by Eugene Pokidov"],
                },
            },
            {
                "type": "property",
                "id": "3101",
                "meta": {
                    "definition": {
                        "type": "date",
                        "attribute": {"id": "2", "name": "Date", "type": "date", "counts": {"templates": {}}},
                    }
                },
                "attributes": {"id": "3101", "name": "My Notebook Field 1 (SK)", "value": "", "values": []},
            },
            {
                "type": "property",
                "id": "3100",
                "meta": {
                    "definition": {
                        "type": "text",
                        "attribute": {"id": "1", "name": "Text", "type": "text", "counts": {"templates": {}}},
                    }
                },
                "attributes": {"id": "3100", "name": "My Notebook Field 2 (SK)", "value": "", "values": []},
            },
        ],
    }


@pytest.fixture()
def set_template_name(entity_factory):
    entity = entity_factory()
    previous_template_name = entity.get_template_name()
    entity.set_template_name('smth.html')
    yield entity, previous_template_name
    entity.set_template_name('entity.html')


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


def test_set_template(set_template_name):
    entity, previous_template_name = set_template_name
    current_template_name = entity.get_template_name()

    assert previous_template_name != current_template_name
    assert current_template_name == 'smth.html'


def test_get_html(entity_factory, snapshot):
    entity = entity_factory(name='name', edited_at=datetime.datetime(2018, 6, 1, 1, 1, 1), description='text')

    entity_html = entity.get_html()

    snapshot.assert_match(entity_html)


def test_update_properties(entity_factory, api_mock, properties, mocker):
    entity = entity_factory()

    assert entity._properties == []

    api_mock.call.return_value.json.return_value = properties

    for item in entity:
        if item.id == '3100':
            item.set_value('555')

    api_mock.call.return_value.json.return_value = {}
    api_mock.call.return_value.json.return_value = properties

    assert entity._properties != []

    request_body = [item.representation_for_update for item in entity._properties if item.is_changed]

    entity.update_properties()

    api_mock.call.assert_has_calls(
        [
            mocker.call(
                method='GET',
                path=(entity._get_endpoint(), entity.eid, 'properties'),
            ),
            mocker.call(
                method='PATCH',
                path=(entity._get_endpoint(), entity.eid, 'properties'),
                params={
                    'digest': None,
                    'force': 'true',
                },
                json={
                    'data': request_body,
                },
            ),
        ],
        any_order=True,
    )


def test_reload_properties(entity_factory, api_mock, properties):
    entity = entity_factory()

    assert entity._properties == []

    api_mock.call.return_value.json.return_value = properties

    for item in entity:
        assert isinstance(item, Property)

    assert entity._properties != []

    api_mock.call.assert_called_once_with(
        method='GET',
        path=(entity._get_endpoint(), entity.eid, 'properties'),
    )


@pytest.mark.parametrize('index', [1, '3100', '3101'])
def test_getitem(api_mock, entity_factory, properties, index):
    entity = entity_factory()

    assert entity._properties == []

    api_mock.call.return_value.json.return_value = properties

    for item in entity:
        assert isinstance(item, Property)

    assert isinstance(entity[index], Property)
    assert entity._properties != []


def test_iter(api_mock, entity_factory, properties):
    entity = entity_factory()

    assert entity._properties == []

    api_mock.call.return_value.json.return_value = properties

    for item in entity:
        assert isinstance(item, Property)

    assert entity._properties != []
