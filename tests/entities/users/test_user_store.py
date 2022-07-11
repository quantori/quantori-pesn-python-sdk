import json

import arrow
import pytest

from users.profile import Profile
from users import User
from users.user_store import UserStore


@pytest.fixture()
def get_response_object(mocker):
    def _f(response):
        mock = mocker.Mock()
        mock.json.return_value = response
        return mock

    return _f


def test_get_by_id(api_mock, user_factory):
    user = user_factory()
    response = {
        'links': {'self': f'https://example.com/api/rest/v1.0/users/{user.id}'},
        'data': {
            'id': user.id,
            'type': 'user',
            'attributes': {
                'isEnabled': True,
                'userId': user.id,
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
                'picture': {'links': {'self': f'https://example.com/api/rest/v1.0/users/{user.id}/picture'}},
                'roles': {
                    'data': [
                        {'id': '1', 'type': 'role'},
                    ]
                },
                'systemGroups': {'links': {'self': f'https://example.com/api/rest/v1.0/users/{user.id}/systemGroups'}},
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = UserStore.get(user.id)

    api_mock.call.assert_called_once_with(method='GET', path=('users', user.id))

    assert isinstance(result, User)
    assert result.id == user.id
    assert result.username == response['data']['attributes']['userName']
    assert result.email == response['data']['attributes']['email']
    assert result.first_name == response['data']['attributes']['firstName']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.last_login_at == arrow.get(response['data']['attributes']['lastLoginAt'])


def test_get_list(api_mock, user_factory):
    user = user_factory()
    response = {
        'links': {
            'self': 'https://example.com/api/rest/v1.0/users?enabled=true&page[offset]=0&page[limit]=20',
            'first': 'https://example.com/api/rest/v1.0/users?enabled=true&page[offset]=0&page[limit]=20',
        },
        'data': [
            {
                'type': 'user',
                'id': user.id,
                'links': {'self': f'https://example.com/api/rest/v1.0/users/{user.id}'},
                'attributes': {
                    'lastLoginAt': '2021-11-02T12:19:13.408Z',
                    'createdAt': '2021-10-22T13:35:40.214Z',
                    'userId': user.id,
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
                    'systemGroups': {
                        'links': {'self': f'https://example.com/api/rest/v1.0/users/{user.id}/systemGroups'}
                    },
                },
            },
        ],
    }
    api_mock.call.return_value.json.return_value = response

    all_users_generator = UserStore.get_list()
    result = list(all_users_generator)
    api_mock.call.assert_called_once_with(
        method='GET',
        path=('users',),
        params={
            'q': '',
            'enabled': json.dumps(response['data'][0]['attributes']['isEnabled']),
            'offset': 0,
            'limit': 20,
        },
    )

    for item, raw_item in zip(result, response['data']):
        assert isinstance(item, User)
        assert item.id == raw_item['id']
        assert item.username == raw_item['attributes']['userName']
        assert item.email == raw_item['attributes']['email']
        assert item.first_name == raw_item['attributes']['firstName']


def test_get_several_pages(api_mock, user_factory, mocker, get_response_object):
    user1 = user_factory()
    user2 = user_factory()
    response1 = {
        'links': {
            'self': 'https://example.com/entities?page[offset]=0&page[limit]=20',
            'next': 'https://example.com/entities?page[offset]=20&page[limit]=20',
        },
        'data': [
            {
                'type': 'user',
                'id': user1.id,
                'links': {'self': f'https://example.com/api/rest/v1.0/users/{user1.id}'},
                'attributes': {
                    'lastLoginAt': '2021-11-02T12:19:13.408Z',
                    'createdAt': '2021-10-22T13:35:40.214Z',
                    'userId': user1.id,
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
                'id': user2.id,
                'links': {'self': f'https://example.com/api/rest/v1.0/users/{user2.id}'},
                'attributes': {
                    'lastLoginAt': '2021-11-02T12:19:13.408Z',
                    'createdAt': '2021-10-22T13:35:40.214Z',
                    'userId': user2.id,
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
                params={
                    'q': '',
                    'enabled': json.dumps(response1['data'][0]['attributes']['isEnabled']),
                    'offset': 0,
                    'limit': 20,
                },
            ),
            mocker.call(
                method='GET',
                path=response1['links']['next'],
            ),
        ]
    )

    for item, raw_item in zip(result, [*response1['data'], *response2['data']]):
        assert isinstance(item, User)
        assert isinstance(item, User)
        assert item.id == raw_item['id']
        assert item.username == raw_item['attributes']['userName']
        assert item.email == raw_item['attributes']['email']
        assert item.first_name == raw_item['attributes']['firstName']


def test_refresh(api_mock, user_factory):
    user = user_factory()

    response = {
        'links': {'self': f'https://example.com/api/rest/v1.0/users/{user.id}'},
        'data': {
            'id': user.id,
            'type': 'user',
            'attributes': {
                'isEnabled': True,
                'userId': user.id,
                'userName': 'foo.bar@perkinelmer.com',
                'email': 'foo.bar@perkinelmer.com',
                'firstName': 'Updated name',
                'lastName': 'bar',
                'alias': 'foo.bar',
                'country': 'USA',
                'organization': 'updated organization',
                'lastLoginAt': '2021-11-29T04:00:02.295Z',
                'createdAt': '2020-07-17T21:48:33.262Z',
            },
            'relationships': {
                'picture': {'links': {'self': f'https://example.com/api/rest/v1.0/users/{user.id}/picture'}},
                'roles': {
                    'data': [
                        {'id': '1', 'type': 'role'},
                    ]
                },
                'systemGroups': {'links': {'self': f'https://example.com/api/rest/v1.0/users/{user.id}/systemGroups'}},
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    UserStore.refresh(user)

    api_mock.call.assert_called_once_with(method='GET', path=('users', user.id))
    assert user.first_name == response['data']['attributes']['firstName']
    assert user.organization == response['data']['attributes']['organization']


def test_get_current_user(api_mock, profile_factory):
    profile = profile_factory()
    response = {
        'links': {'self': 'https://example.com/api/rest/v1.0/profiles/me'},
        'data': {
            'type': 'profile',
            'id': profile.id,
            'links': {'self': 'https://example.com/api/rest/v1.0/profiles/me'},
            'attributes': {
                'userId': profile.id,
                'firstName': 'Test',
                'lastName': 'Test',
                'email': 'foo.bar@perkinelmer.com',
                'createdAt': '2022-04-29T18:38:54.731972Z',
                'tenant': 'tenant',
                'alert': {},
                'roles': [{'id': '1', 'name': 'System Admin'}, {'id': '3', 'name': 'Standard User'}],
                'licenses': [
                    {
                        'id': 'SIGNALS_NOTEBOOK',
                        'name': 'SIGNALS_NOTEBOOK',
                        'expiresAt': '2022-10-20T00:00Z',
                        'valid': True,
                        'hasServiceExpired': False,
                        'hasUserFound': False,
                        'hasUserActivated': False,
                    }
                ],
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = UserStore.get_current_user()

    api_mock.call.assert_called_once_with(method='GET', path=('profiles', 'me'))

    assert isinstance(result, Profile)
    assert result.id == response['data']['id']
    assert result.email == response['data']['attributes']['email']
    assert result.first_name == response['data']['attributes']['firstName']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.tenant == response['data']['attributes']['tenant']
