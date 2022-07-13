import json
import mimetypes

import arrow

from signals_notebook.common_types import File, ObjectType
from signals_notebook.users.group import Group
from signals_notebook.users.role import Role
from signals_notebook.users.user import Profile, User


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

    result = User.get(user.id)

    api_mock.call.assert_called_once_with(method='GET', path=('users', user.id))

    assert isinstance(result, User)
    assert result.id == user.id
    assert result.username == response['data']['attributes']['userName']
    assert result.email == response['data']['attributes']['email']
    assert result.first_name == response['data']['attributes']['firstName']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.last_login_at == arrow.get(response['data']['attributes']['lastLoginAt'])
    assert result._relationships == response['data']['relationships']


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

    all_users_generator = User.get_list()
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
        assert item._relationships == raw_item['relationships']


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

    result_generator = User.get_list()

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

    User.refresh(user)

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

    result = User.get_current_user()

    api_mock.call.assert_called_once_with(method='GET', path=('profiles', 'me'))

    assert isinstance(result, Profile)
    assert result.id == response['data']['id']
    assert result.email == response['data']['attributes']['email']
    assert result.first_name == response['data']['attributes']['firstName']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.tenant == response['data']['attributes']['tenant']


def test_get_roles(api_mock, user_factory, role_factory):
    user = user_factory()
    role = role_factory()

    relationships = {
        'picture': {'links': {'self': f'https://example.com/api/rest/v1.0/users/{user.id}/picture'}},
        'roles': {
            'data': [
                {'id': role.id, 'type': 'role'},
            ]
        },
        'systemGroups': {'links': {'self': f'https://example.com/api/rest/v1.0/users/{user.id}/systemGroups'}},
    }
    role_response = {
        'links': {'self': 'https://example.com/api/rest/v1.0/roles/1'},
        'data': {
            'type': 'role',
            'id': role.id,
            'links': {'self': 'https://example.com/api/rest/v1.0/roles/1'},
            'attributes': {
                'id': role.id,
                'name': 'System Admin',
                'description': 'Users with this role have all privileges.',
                'privileges': {
                    'canMoveExperiments': 'true',
                    'canManageSystemTemplates': 'true',
                    'canTrashRequests': 'true',
                    'canTrashSamples': 'true',
                    'canShare': 'true',
                    'canAddMaterials': 'true',
                    'canTrashExperiments': 'true',
                    'canTrashMaterials': 'true',
                    'canTrashNotebooks': 'true',
                    'canViewMaterials': 'true',
                    'canManageMaterialLibraries': 'true',
                    'canShareTemplates': 'true',
                    'canManageAttributes': 'true',
                    'canManageGroups': 'true',
                    'canSearchElnArchive': 'true',
                    'canConfigure': 'true',
                    'canEditMaterials': 'true',
                },
            },
        },
    }
    user.set_relationships(relationships)

    api_mock.call.return_value.json.return_value = role_response

    roles = user.roles

    api_mock.call.assert_called_once_with(method='GET', path=('roles', role.id))

    assert isinstance(roles, list)
    for role in roles:
        assert isinstance(role, Role)


def test_create(api_mock, role_factory):
    role = role_factory()
    response = {
        'links': {'self': 'https://snb.perkinelmer.net/api/rest/v1.0/users/100'},
        'data': {
            'id': '100',
            'type': 'user',
            'attributes': {
                'isEnabled': True,
                'userId': '100',
                'userName': 'foo.bar@perkinelmer.com',
                'email': 'unique2@quantori.com',
                'firstName': 'first_name',
                'lastName': 'last_name',
                'alias': 'alias',
                'country': 'USA',
                'organization': 'orga',
                'lastLoginAt': '2021-11-29T04:00:02.295Z',
                'createdAt': '2020-07-17T21:48:33.262Z',
            },
        },
    }

    api_mock.call.return_value.json.return_value = response

    result = User.create(
        alias='alias',
        country='USA',
        email='unique2@quantori.com',
        first_name='first_name',
        last_name='last_name',
        organization='orga',
        roles=[role],
    )

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('users',),
        json={
            'data': {
                'attributes': {
                    'alias': 'alias',
                    'country': 'USA',
                    'emailAddress': 'unique2@quantori.com',
                    'firstName': 'first_name',
                    'lastName': 'last_name',
                    'organization': 'orga',
                    'roles': [{'id': role.id, 'name': role.name}],
                },
            }
        },
    )

    assert isinstance(result, User)
    assert result.id == response['data']['attributes']['userId']
    assert result.alias == response['data']['attributes']['alias']
    assert result.country == response['data']['attributes']['country']
    assert result.first_name == response['data']['attributes']['firstName']
    assert result.last_name == response['data']['attributes']['lastName']
    assert result.organization == response['data']['attributes']['organization']


def test_save(api_mock, user_factory):
    user = user_factory()
    new_first_name = 'Update first name'
    assert user.first_name != new_first_name

    user.first_name = new_first_name

    user.save()

    api_mock.call.assert_called_once_with(
        method='PATCH',
        path=('users', user.id),
        json={
            'data': {
                'attributes': {
                    'alias': user.alias,
                    'country': user.country,
                    'firstName': 'Update first name',
                    'lastName': user.last_name,
                    'organization': user.organization,
                },
            },
        },
    )
    assert user.first_name == new_first_name


def test_delete(api_mock, user_factory):
    user = user_factory()
    user.delete()

    api_mock.call.assert_called_once_with(
        method='DELETE',
        path=('users', user.id),
    )


def test_picture(api_mock, user_factory):
    content_type = 'image/jpeg'
    content = b'image'

    user = user_factory()
    extension = mimetypes.guess_extension(content_type)
    file_name = f'{user.first_name}_{user.last_name}{extension}'

    api_mock.call.return_value.content = content
    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    result = user.picture

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('users', user.id, 'picture'),
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type


def test_get_system_groups(api_mock, user_factory):
    user = user_factory()
    response = {
        'links': {'self': 'https://quantori.signalsnotebook.perkinelmer.cloud/api/rest/v1.0/users/101/systemGroups'},
        'data': [
            {
                'type': 'group',
                'id': '101',
                'links': {'self': 'https://quantori.signalsnotebook.perkinelmer.cloud/api/rest/v1.0/groups/101'},
                'attributes': {
                    'isSystem': True,
                    'id': '101',
                    'eid': 'group:101',
                    'name': 'Administrators',
                    'description': 'Group containing all administrators',
                    'createdAt': '2021-10-22T13:35:58.444Z',
                    'editedAt': '2021-10-22T13:35:58.444Z',
                    'type': 'group',
                    'digest': '13385924',
                },
            },
            {
                'type': 'group',
                'id': '102',
                'links': {'self': 'https://quantori.signalsnotebook.perkinelmer.cloud/api/rest/v1.0/groups/102'},
                'attributes': {
                    'isSystem': True,
                    'id': '102',
                    'eid': 'group:102',
                    'name': 'All users',
                    'description': 'Group containing all users',
                    'createdAt': '2021-10-22T13:35:58.625Z',
                    'editedAt': '2021-10-22T13:35:58.625Z',
                    'type': 'group',
                    'digest': '46357805',
                },
            },
        ],
    }
    api_mock.call.return_value.json.return_value = response

    result = user.groups

    api_mock.call.assert_called_once_with(method='GET', path=('users', user.id, 'systemGroups'))

    for item, raw_item in zip(result, response['data']):
        assert isinstance(item, Group)
        assert item.id == raw_item['id']
        assert item.type == ObjectType.GROUP
        assert item.is_system == raw_item['attributes']['isSystem']
        assert item.name == raw_item['attributes']['name']
        assert item.description == raw_item['attributes']['description']
        assert item.created_at == arrow.get(raw_item['attributes']['createdAt'])
        assert item.edited_at == arrow.get(raw_item['attributes']['editedAt'])
        assert item.digest == raw_item['attributes']['digest']
