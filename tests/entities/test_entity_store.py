from datetime import datetime

import arrow
import pytest

from signals_notebook.entities import Experiment, Notebook
from signals_notebook.entities.entity_store import EntityStore
from signals_notebook.types import EID, EntitySubtype, ObjectType


@pytest.fixture()
def get_response_object(mocker):
    def _f(response):
        mock = mocker.Mock()
        mock.json.return_value = response
        return mock
    return _f


@pytest.mark.parametrize(
    'eid,entity_type,expected_class',
    [
        (EID('experiment:878a87ca-3777-4692-8561-a4a81ccfd85d'), EntitySubtype.EXPERIMENT, Experiment),
        (EID('journal:878a87ca-3777-4692-8561-a4a81ccfd85d'), EntitySubtype.NOTEBOOK, Notebook),
    ],
)
def test_get(api_mock, eid, entity_type, expected_class):
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'eid': eid,
                'name': 'My experiment',
                'description': 'test description',
                'type': entity_type,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '1234234',
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = EntityStore.get(eid)

    api_mock.call.assert_called_once_with(method='GET', path=('entities', eid))

    assert isinstance(result, expected_class)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.description == response['data']['attributes']['description']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


@pytest.mark.parametrize('digest, force', [('1234234', False), (None, True)])
def test_delete(api_mock, digest, force):
    eid = EID('experiment:e360eea6-b331-4c6f-b340-6d0eaa7eb070')

    EntityStore.delete(eid, digest, force)

    api_mock.call.assert_called_once_with(
        method='DELETE',
        path=('entities', eid),
        params={
            'digest': digest,
            'force': 'true' if force else 'false',
        },
    )


def test_get_list_with_params(api_mock):
    eid1 = EID('experiment:878a87ca-3777-4692-8561-a4a81ccfd85d')
    eid2 = EID('experiment:52062e1d-7e03-464f-8caf-d7ed93261213')
    response = {
        'links': {'self': f'https://example.com/{eid1}'},
        'data': [
            {
                'type': ObjectType.ENTITY,
                'id': eid1,
                'links': {'self': f'https://example.com/{eid1}'},
                'attributes': {
                    'eid': eid1,
                    'name': 'My experiment 1',
                    'description': 'test description 1',
                    'type': EntitySubtype.EXPERIMENT,
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
                    'name': 'My experiment 2',
                    'description': 'test description 2',
                    'type': EntitySubtype.EXPERIMENT,
                    'createdAt': '2021-09-06T03:12:35.129Z',
                    'editedAt': '2021-09-06T15:22:47.309Z',
                    'digest': '34563546',
                },
            },
        ],
    }
    api_mock.call.return_value.json.return_value = response

    result_generator = EntityStore.get_list(
        include_types=[EntitySubtype.EXPERIMENT, EntitySubtype.TEXT],
        exclude_types=[EntitySubtype.NOTEBOOK],
        include_options=[EntityStore.IncludeOptions.MINE, EntityStore.IncludeOptions.STARRED],
        modified_after=datetime(2022, 2, 24, 6, 0),
        modified_before=datetime(2022, 3, 2, 15, 45, 12),
    )

    api_mock.call.assert_not_called()

    result = list(result_generator)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities',),
        params={
            'includeTypes': 'experiment,text',
            'excludeTypes': 'journal',
            'includeOptions': 'mine,starred',
            'start': '2022-02-24T06:00:00',
            'end': '2022-03-02T15:45:12',
        },
    )

    for item, raw_item in zip(result, response['data']):
        assert isinstance(item, Experiment)
        assert item.eid == raw_item['id']
        assert item.digest == raw_item['attributes']['digest']
        assert item.name == raw_item['attributes']['name']
        assert item.description == raw_item['attributes']['description']
        assert item.created_at == arrow.get(raw_item['attributes']['createdAt'])
        assert item.edited_at == arrow.get(raw_item['attributes']['editedAt'])


def test_get_list_without_params(api_mock):
    eid1 = EID('experiment:878a87ca-3777-4692-8561-a4a81ccfd85d')
    eid2 = EID('experiment:52062e1d-7e03-464f-8caf-d7ed93261213')
    response = {
        'links': {'self': f'https://example.com/{eid1}'},
        'data': [
            {
                'type': ObjectType.ENTITY,
                'id': eid1,
                'links': {'self': f'https://example.com/{eid1}'},
                'attributes': {
                    'eid': eid1,
                    'name': 'My experiment 1',
                    'description': 'test description 1',
                    'type': EntitySubtype.EXPERIMENT,
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
                    'name': 'My experiment 2',
                    'description': 'test description 2',
                    'type': EntitySubtype.EXPERIMENT,
                    'createdAt': '2021-09-06T03:12:35.129Z',
                    'editedAt': '2021-09-06T15:22:47.309Z',
                    'digest': '34563546',
                },
            },
        ],
    }
    api_mock.call.return_value.json.return_value = response

    result_generator = EntityStore.get_list()

    api_mock.call.assert_not_called()

    result = list(result_generator)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities',),
        params=None,
    )

    for item, raw_item in zip(result, response['data']):
        assert isinstance(item, Experiment)
        assert item.eid == raw_item['id']
        assert item.digest == raw_item['attributes']['digest']
        assert item.name == raw_item['attributes']['name']
        assert item.description == raw_item['attributes']['description']
        assert item.created_at == arrow.get(raw_item['attributes']['createdAt'])
        assert item.edited_at == arrow.get(raw_item['attributes']['editedAt'])


def test_get_several_pages(api_mock, mocker, get_response_object):
    eid1 = EID('experiment:878a87ca-3777-4692-8561-a4a81ccfd85d')
    eid2 = EID('experiment:52062e1d-7e03-464f-8caf-d7ed93261213')
    response1 = {
        'links': {
            'self': f'https://example.com/entities?page[offset]=0&page[limit]=20',
            'next': f'https://example.com/entities?page[offset]=20&page[limit]=20',
        },
        'data': [
            {
                'type': ObjectType.ENTITY,
                'id': eid1,
                'links': {'self': f'https://example.com/{eid1}'},
                'attributes': {
                    'eid': eid1,
                    'name': 'My experiment 1',
                    'description': 'test description 1',
                    'type': EntitySubtype.EXPERIMENT,
                    'createdAt': '2020-09-06T03:12:35.129Z',
                    'editedAt': '2020-09-06T15:22:47.309Z',
                    'digest': '53263456',
                },
            },
        ],
    }
    response2 = {
        'links': {
            'prev': f'https://example.com/entities?page[offset]=0&page[limit]=20',
            'self': f'https://example.com/entities?page[offset]=20&page[limit]=20',
        },
        'data': [
            {
                'type': ObjectType.ENTITY,
                'id': eid2,
                'links': {'self': f'https://example.com/{eid2}'},
                'attributes': {
                    'eid': eid2,
                    'name': 'My experiment 2',
                    'description': 'test description 2',
                    'type': EntitySubtype.EXPERIMENT,
                    'createdAt': '2021-09-06T03:12:35.129Z',
                    'editedAt': '2021-09-06T15:22:47.309Z',
                    'digest': '34563546',
                },
            },
        ],
    }

    api_mock.call.side_effect = [get_response_object(response1), get_response_object(response2)]

    result_generator = EntityStore.get_list()

    api_mock.call.assert_not_called()

    result = list(result_generator)

    api_mock.call.assert_has_calls(
        [
            mocker.call(
                method='GET',
                path=('entities',),
                params=None,
            ),
            mocker.call(
                method='GET',
                path=response1['links']['next'],
            ),
        ]
    )

    for item, raw_item in zip(result, [*response1['data'], *response2['data']]):
        assert isinstance(item, Experiment)
        assert item.eid == raw_item['id']
        assert item.digest == raw_item['attributes']['digest']
        assert item.name == raw_item['attributes']['name']
        assert item.description == raw_item['attributes']['description']
        assert item.created_at == arrow.get(raw_item['attributes']['createdAt'])
        assert item.edited_at == arrow.get(raw_item['attributes']['editedAt'])
