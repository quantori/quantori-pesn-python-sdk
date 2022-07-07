import json

import arrow
import pytest

from signals_notebook.entities.users.group import Group, GroupRequestBody


def test_get_list(api_mock):
    response = {
        "links": {"self": "https://snb.perkinelmer.net/api/rest/v1.0/groups"},
        "data": [
            {
                "id": "1",
                "type": "group",
                "attributes": {
                    "id": "1",
                    "name": "TestSys",
                    "description": "TestSys",
                    "createdAt": "2019-12-02T04:58:45.069Z",
                    "editedAt": "2019-12-02T04:58:45.069Z",
                    "type": "group",
                    "digest": "23eeab9d8c63bb438cf56596d4b7f589",
                    "isSystem": "true",
                },
            },
            {
                "id": "2",
                "type": "group",
                "attributes": {
                    "id": "2",
                    "name": "Administrator",
                    "description": "Administrator",
                    "createdAt": "2019-12-02T04:58:45.069Z",
                    "editedAt": "2019-12-02T04:58:45.069Z",
                    "type": "group",
                    "digest": "23eeab9d8c63bb438cf56596d4b7f589",
                    "isSystem": "true",
                },
            },
        ],
    }
    api_mock.call.return_value.json.return_value = response

    all_users_generator = Group.get_list()
    result = list(all_users_generator)
    api_mock.call.assert_called_once_with(
        method='GET',
        path=('groups',),
    )

    for item, raw_item in zip(result, response['data']):
        assert isinstance(item, Group)
        assert item.id == raw_item['id']
        assert item.name == raw_item['attributes']['name']
        assert item.description == raw_item['attributes']['description']
        assert item.created_at == arrow.get(raw_item['attributes']['createdAt'])
        assert item.edited_at == arrow.get(raw_item['attributes']['editedAt'])
        assert item.is_system == json.loads(raw_item['attributes']['isSystem'])


def test_get_by_id(api_mock, group_factory):
    group = group_factory()
    response = {
        "links": {"self": "https://example.com/api/rest/v1.0/groups/103"},
        "data": {
            "id": group.id,
            "type": "group",
            "attributes": {
                "id": group.id,
                "name": "TestSys",
                "description": "TestSys",
                "createdAt": "2019-12-02T04:58:45.069Z",
                "editedAt": "2019-12-02T04:58:45.069Z",
                "type": "group",
                "digest": "23eeab9d8c63bb438cf56596d4b7f589",
                "isSystem": "true",
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = Group.get(group.id)

    api_mock.call.assert_called_once_with(method='GET', path=('groups', group.id))

    assert isinstance(result, Group)
    assert result.id == response['data']['id']
    assert result.name == response['data']['attributes']['name']
    assert result.description == response['data']['attributes']['description']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])
    assert result.is_system == json.loads(response['data']['attributes']['isSystem'])


def test_create(api_mock):
    response = {
        "links": {"self": "https://example.com/api/rest/v1.0/groups/103"},
        "data": {
            "id": "103",
            "type": "group",
            "attributes": {
                "id": "103",
                "name": "name",
                "description": "description",
                "createdAt": "2019-12-02T04:58:45.069Z",
                "editedAt": "2019-12-02T04:58:45.069Z",
                "type": "group",
                "digest": "23eeab9d8c63bb438cf56596d4b7f589",
                "isSystem": "true",
            },
        },
    }
    new_user_body = GroupRequestBody(
        is_system=True,
        name='name',
        description='description',
    )
    api_mock.call.return_value.json.return_value = response

    result = Group.create(request=new_user_body)

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('groups',),
        json={
            'data': {
                'attributes': new_user_body.dict(by_alias=True),
            }
        },
    )

    assert isinstance(result, Group)
    assert result.id == response['data']['id']
    assert result.name == response['data']['attributes']['name']
    assert result.description == response['data']['attributes']['description']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])
    assert result.is_system == json.loads(response['data']['attributes']['isSystem'])


def test_save(api_mock, group_factory):
    group = group_factory()
    new_name = 'Update name'
    assert group.name != new_name

    group.name = new_name

    group.save()

    api_mock.call.assert_called_once_with(
        method='PATCH',
        path=('groups', group.id),
        params={
            'force': json.dumps(True),
        },
        json={
            'data': {
                'attributes': {
                    'name': group.name,
                    'description': group.description,
                },
            },
        },
    )
    assert group.name == new_name