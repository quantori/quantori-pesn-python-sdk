import json

from users.profile import Role


def test_get_by_id(api_mock, role_factory):
    role = role_factory()
    response = {
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
    api_mock.call.return_value.json.return_value = response

    result = Role.get(role.id)

    api_mock.call.assert_called_once_with(method='GET', path=('roles', role.id))

    json_privileges = {k: json.dumps(v) for k, v in result.privileges.dict(by_alias=True).items()}

    assert isinstance(result, Role)
    assert result.id == role.id
    assert result.name == response['data']['attributes']['name']
    assert result.description == response['data']['attributes']['description']
    assert json_privileges == response['data']['attributes']['privileges']


def test_get_list(api_mock):
    response = {
        'links': {'self': 'https://example.com/api/rest/v1.0/roles'},
        'data': [
            {
                'type': 'role',
                'id': '1',
                'links': {'self': 'https://example.com/api/rest/v1.0/roles/1'},
                'attributes': {
                    'id': '1',
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
            {
                'type': 'role',
                'id': '2',
                'links': {'self': 'https://example.com/api/rest/v1.0/roles/2'},
                'attributes': {
                    'id': '2',
                    'name': 'Config Admin',
                    'description': 'Users with this role have privileges for accessing SNConfig and managing metadata.',
                    'privileges': {
                        'canMoveExperiments': 'true',
                        'canManageSystemTemplates': 'false',
                        'canTrashRequests': 'true',
                        'canTrashSamples': 'true',
                        'canShare': 'true',
                        'canAddMaterials': 'false',
                        'canTrashExperiments': 'true',
                        'canTrashMaterials': 'true',
                        'canTrashNotebooks': 'true',
                        'canViewMaterials': 'false',
                        'canManageMaterialLibraries': 'true',
                        'canShareTemplates': 'true',
                        'canManageAttributes': 'true',
                        'canManageGroups': 'true',
                        'canSearchElnArchive': 'false',
                        'canConfigure': 'true',
                        'canEditMaterials': 'true',
                    },
                },
            },
        ],
    }
    api_mock.call.return_value.json.return_value = response

    all_roles = Role.get_list()
    result = list(all_roles)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('roles',),
    )

    for item, raw_item in zip(result, response['data']):
        json_privileges = {k: json.dumps(v) for k, v in item.privileges.dict(by_alias=True).items()}

        assert isinstance(item, Role)
        assert item.id == raw_item['id']
        assert item.name == raw_item['attributes']['name']
        assert item.description == raw_item['attributes']['description']
        assert json_privileges == raw_item['attributes']['privileges']
