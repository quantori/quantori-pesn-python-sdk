import arrow
import pytest

from signals_notebook.entities.users.user import User
from signals_notebook.entities.users.user_store import UserStore


@pytest.fixture()
def get_response_object(mocker):
    def _f(response):
        mock = mocker.Mock()
        mock.json.return_value = response
        return mock

    return _f


def test_get_by_id(api_mock, eid):
    response = {
        'links': {'self': f'https://example.com/api/rest/v1.0/users/{eid}'},
        'data': {
            'id': eid,
            'type': 'user',
            'attributes': {
                'isEnabled': True,
                'userId': eid,
                'userName': 'foo.bar@perkinelmer.com',
                'email': 'foo.bar@perkinelmer.com',
                'firstName': 'foo',
                'lastName': 'bar',
                'alias': 'foo.bar',
                'country': 'USA',
                'organization': 'Perkinelmer',
                'lastLoginAt': '2021-11-29T04:00:02.295Z',
                'createdAt': '2020-07-17T21:48:33.262Z',
            },
            'relationships': {
                'picture': {'links': {'self': f'https://example.com/api/rest/v1.0/users/{eid}/picture'}},
                'roles': {
                    'data': [
                        {'id': '1', 'type': 'role'},
                    ]
                },
                'systemGroups': {'links': {'self': f'https://example.com/api/rest/v1.0/users/{eid}/systemGroups'}},
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = UserStore.get(eid)

    api_mock.call.assert_called_once_with(method='GET', path=('users', eid))

    assert isinstance(result, User)
    assert result.id == eid
    assert result.username == response['data']['attributes']['userName']
    assert result.email == response['data']['attributes']['email']
    assert result.first_name == response['data']['attributes']['firstName']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.last_login_at == arrow.get(response['data']['attributes']['lastLoginAt'])


def test_get_list(api_mock):
    response = {
        'links': {
            'self': 'https://example.com/api/rest/v1.0/users?enabled=true&page[offset]=0&page[limit]=20',
            'first': 'https://example.com/api/rest/v1.0/users?enabled=true&page[offset]=0&page[limit]=20',
        },
        'data': [
            {
                'type': 'user',
                'id': '100',
                'links': {'self': 'https://example.com/api/rest/v1.0/users/100'},
                'attributes': {
                    'lastLoginAt': '2021-11-02T12:19:13.408Z',
                    'createdAt': '2021-10-22T13:35:40.214Z',
                    'userId': '100',
                    'userName': 'foo.bar@perkinelmer.com',
                    'email': 'foo.bar@perkinelmer.com',
                    'firstName': 'Stephen',
                    'lastName': 'Tharp',
                    'country': 'USA',
                    'organization': 'quantori',
                    'isEnabled': True,
                },
                'relationships': {
                    'roles': {
                        'data': [
                            {
                                'type': 'role',
                                'id': '1',
                                'meta': {'links': {'self': 'https://example.com/api/rest/v1.0/roles/1'}},
                            },
                            {
                                'type': 'role',
                                'id': '3',
                                'meta': {'links': {'self': 'https://example.com/api/rest/v1.0/roles/3'}},
                            },
                        ]
                    },
                    'systemGroups': {'links': {'self': 'https://example.com/api/rest/v1.0/users/100/systemGroups'}},
                },
            },
        ],
    }
    api_mock.call.return_value.json.return_value = response

    all_users_generator = UserStore.get_list()
    result = list(all_users_generator)
    api_mock.call.assert_called_once_with(method='GET', path=('users',))

    for item, raw_item in zip(result, response['data']):
        assert isinstance(item, User)
        assert item.id == raw_item['id']
        assert item.username == raw_item['attributes']['userName']
        assert item.email == raw_item['attributes']['email']
        assert item.first_name == raw_item['attributes']['firstName']


def test_get_several_pages(api_mock, mocker, get_response_object):
    response1 = {
        'links': {
            'self': 'https://example.com/entities?page[offset]=0&page[limit]=20',
            'next': 'https://example.com/entities?page[offset]=20&page[limit]=20',
        },
        'data': [
            {
                'type': 'user',
                'id': '1',
                'links': {'self': 'https://example.com/api/rest/v1.0/users/1'},
                'attributes': {
                    'lastLoginAt': '2021-11-02T12:19:13.408Z',
                    'createdAt': '2021-10-22T13:35:40.214Z',
                    'userId': '1',
                    'userName': 'foo.bar@perkinelmer.com',
                    'email': 'foo.bar@perkinelmer.com',
                    'firstName': 'Stephen',
                    'lastName': 'Tharp',
                    'country': 'USA',
                    'organization': 'quantori',
                    'isEnabled': True,
                },
                'relationships': {
                    'roles': {
                        'data': [
                            {
                                'type': 'role',
                                'id': '1',
                                'meta': {'links': {'self': 'https://example.com/api/rest/v1.0/roles/1'}},
                            },
                            {
                                'type': 'role',
                                'id': '3',
                                'meta': {'links': {'self': 'https://example.com/api/rest/v1.0/roles/3'}},
                            },
                        ]
                    },
                    'systemGroups': {'links': {'self': 'https://example.com/api/rest/v1.0/users/100/systemGroups'}},
                },
            },
        ],
    }
    response2 = {
        'links': {
            'prev': 'https://example.com/entities?page[offset]=0&page[limit]=20',
            'self': 'https://example.com/entities?page[offset]=20&page[limit]=20',
        },
        'data': [
            {
                'type': 'user',
                'id': '2',
                'links': {'self': f'https://example.com/api/rest/v1.0/users/2'},
                'attributes': {
                    'lastLoginAt': '2021-11-02T12:19:13.408Z',
                    'createdAt': '2021-10-22T13:35:40.214Z',
                    'userId': '2',
                    'userName': 'foo.bar@perkinelmer.com',
                    'email': 'foo.bar@perkinelmer.com',
                    'firstName': 'Stephen',
                    'lastName': 'Tharp',
                    'country': 'USA',
                    'organization': 'quantori',
                    'isEnabled': True,
                },
                'relationships': {
                    'roles': {
                        'data': [
                            {
                                'type': 'role',
                                'id': '1',
                                'meta': {'links': {'self': 'https://example.com/api/rest/v1.0/roles/1'}},
                            },
                            {
                                'type': 'role',
                                'id': '3',
                                'meta': {'links': {'self': 'https://example.com/api/rest/v1.0/roles/3'}},
                            },
                        ]
                    },
                    'systemGroups': {'links': {'self': 'https://example.com/api/rest/v1.0/users/100/systemGroups'}},
                },
            },
        ],
    }

    api_mock.call.side_effect = [get_response_object(response1), get_response_object(response2)]

    result_generator = UserStore.get_list()

    api_mock.call.assert_not_called()

    result = list(result_generator)

    api_mock.call.assert_has_calls(
        [
            mocker.call(
                method='GET',
                path=('users',),
            ),
            mocker.call(
                method='GET',
                path=response1['links']['next'],
            ),
        ]
    )

    for item, raw_item in zip(result, [*response1['data'], *response2['data']]):
        assert isinstance(item, User)
        assert item.eid == raw_item['id']
        assert item.digest == raw_item['attributes']['digest']
        assert item.name == raw_item['attributes']['name']
        assert item.description == raw_item['attributes']['description']
        assert item.created_at == arrow.get(raw_item['attributes']['createdAt'])
        assert item.edited_at == arrow.get(raw_item['attributes']['editedAt'])
