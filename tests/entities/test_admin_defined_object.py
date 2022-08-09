import datetime
import json

import arrow
import pytest

from signals_notebook.common_types import EntityType, ObjectType
from signals_notebook.entities import ChemicalDrawing, Entity, Text, AdminDefinedObject


@pytest.fixture()
def templates():
    return {
        'links': {
            'self': 'https://ex.com/api/rest/v1.0/'
            'entities?includeTypes=admin_defined_object&includeOptions=template&page[offset]=0&page[limit]=20',
            'first': 'https://ex.com/api/rest/v1.0/'
            'entities?includeTypes=admin_defined_object&includeOptions=template&page[offset]=0&page[limit]=20',
        },
        'data': [
            {
                'type': 'entity',
                'id': 'admin_defined_object:d4d25125-5665-4c89-b9b6-049b44e1355e',
                'links': {
                    'self': 'https://ex.com/api/rest/v1.0/entities/admin_defined_object:d4d25125-5665-4c89-b9b6-049b44e1355e'
                },
                'attributes': {
                    'id': 'admin_defined_object:d4d25125-5665-4c89-b9b6-049b44e1355e',
                    'eid': 'admin_defined_object:d4d25125-5665-4c89-b9b6-049b44e1355e',
                    'name': 'DEFAULT_admin_defined_object',
                    'description': '',
                    'createdAt': '2021-10-22T13:36:01.730Z',
                    'editedAt': '2022-07-27T07:25:41.960Z',
                    'type': 'ado',
                    'digest': '68929861',
                    'fields': {'Description': {'value': ''}, 'Name': {'value': 'DEFAULT_admin_defined_object'}},
                    'flags': {'canEdit': True},
                },
            }
        ],
    }


@pytest.mark.parametrize('description', ['test description', None])
@pytest.mark.parametrize('digest, force', [('1234234', False), (None, True)])
def test_create(api_mock, description, digest, force, eid_factory):
    eid = eid_factory(type=EntityType.ADO)
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'eid': eid,
                'name': 'My admin_defined_object',
                'description': description,
                'type': EntityType.ADO,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': digest,
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = AdminDefinedObject.create(name='My admin_defined_object', description=description, digest=digest, force=force)

    request_body = {
        'data': {
            'type': EntityType.ADO,
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

    assert isinstance(result, AdminDefinedObject)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.description == response['data']['attributes']['description']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_create_with_ancestors(api_mock, notebook_factory, eid_factory):
    notebook = notebook_factory()
    eid = eid_factory(type=EntityType.ADO)
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'eid': eid,
                'name': 'My admin_defined_object',
                'description': 'Some description',
                'type': EntityType.ADO,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '123144',
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = AdminDefinedObject.create(name='My admin_defined_object', description='Some description', notebook=notebook, force=True)

    request_body = {
        'data': {
            'type': EntityType.ADO,
            'attributes': {
                'name': response['data']['attributes']['name'],
                'description': response['data']['attributes']['description'],
            },
            'relationships': {
                'ancestors': {
                    'data': [
                        {
                            'id': notebook.eid,
                            'type': EntityType.NOTEBOOK,
                        }
                    ]
                }
            },
        }
    }

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('entities',),
        params={
            'digest': None,
            'force': 'true',
        },
        json=request_body,
    )

    assert isinstance(result, AdminDefinedObject)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.description == response['data']['attributes']['description']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_create_with_template(api_mock, admin_defined_object_factory, eid_factory):
    template = admin_defined_object_factory()
    eid = eid_factory(type=EntityType.ADO)
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'eid': eid,
                'name': 'My admin_defined_object',
                'description': 'Some description',
                'type': EntityType.ADO,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '123144',
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = AdminDefinedObject.create(name='My admin_defined_object', description='Some description', template=template, force=True)

    request_body = {
        'data': {
            'type': EntityType.ADO,
            'attributes': {
                'name': response['data']['attributes']['name'],
                'description': response['data']['attributes']['description'],
            },
            'relationships': {
                'template': {
                    'data': {
                        'id': template.eid,
                        'type': EntityType.ADO,
                    }
                }
            },
        }
    }

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('entities',),
        params={
            'digest': None,
            'force': 'true',
        },
        json=request_body,
    )

    assert isinstance(result, AdminDefinedObject)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.description == response['data']['attributes']['description']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


@pytest.mark.parametrize('force', [True, False])
def test_add_children(api_mock, admin_defined_object_factory, force, eid_factory):
    admin_defined_object = admin_defined_object_factory()
    eid = eid_factory(type=EntityType.ADO)
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'eid': eid,
                'name': 'My text',
                'description': '',
                'type': EntityType.TEXT,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '123144',
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = admin_defined_object.add_child(
        name='My text',
        content=b'Some text',
        content_type='text/plain',
        force=force,
    )

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('entities', admin_defined_object.eid, 'children', 'My text.txt'),
        params={
            'digest': None if force else admin_defined_object.digest,
            'force': 'true' if force else 'false',
        },
        headers={
            'Content-Type': 'text/plain',
        },
        data=b'Some text',
    )

    assert isinstance(result, Text)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.description == response['data']['attributes']['description']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_get_children__one_page(api_mock, admin_defined_object_factory, eid_factory):
    admin_defined_object = admin_defined_object_factory()
    text_eid = eid_factory(type=EntityType.TEXT)
    chem_draw_eid = eid_factory(type=EntityType.CHEMICAL_DRAWING)
    unknown_eid = eid_factory(type='unknown')
    response = {
        'links': {'self': f'https://example.com/{admin_defined_object.eid}/children'},
        'data': [
            {
                'type': ObjectType.ENTITY,
                'id': text_eid,
                'links': {'self': f'https://example.com/{text_eid}'},
                'attributes': {
                    'eid': text_eid,
                    'name': 'My text',
                    'description': '',
                    'type': EntityType.TEXT,
                    'createdAt': '2019-09-06T03:12:35.129Z',
                    'editedAt': '2019-09-06T15:22:47.309Z',
                    'digest': '123144',
                },
            },
            {
                'type': ObjectType.ENTITY,
                'id': chem_draw_eid,
                'links': {'self': f'https://example.com/{chem_draw_eid}'},
                'attributes': {
                    'eid': chem_draw_eid,
                    'name': 'Some reactions',
                    'description': '',
                    'type': EntityType.CHEMICAL_DRAWING,
                    'createdAt': '2019-09-06T03:12:35.129Z',
                    'editedAt': '2019-09-06T15:22:47.309Z',
                    'digest': '123144',
                },
            },
            {
                'type': ObjectType.ENTITY,
                'id': unknown_eid,
                'links': {'self': f'https://example.com/{unknown_eid}'},
                'attributes': {
                    'eid': unknown_eid,
                    'name': 'Some reactions',
                    'description': '',
                    'type': 'unknown',
                    'createdAt': '2019-09-06T03:12:35.129Z',
                    'editedAt': '2019-09-06T15:22:47.309Z',
                    'digest': '123144',
                },
            },
        ],
    }
    api_mock.call.return_value.json.return_value = response

    result = list(admin_defined_object.get_children())

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', admin_defined_object.eid, 'children'),
        params={'order': 'layout'},
    )

    assert isinstance(result[0], Text)
    assert result[0].eid == text_eid

    assert isinstance(result[1], ChemicalDrawing)
    assert result[1].eid == chem_draw_eid

    assert isinstance(result[2], Entity)
    assert result[2].eid == unknown_eid


def test_get_children__several_pages(mocker, api_mock, admin_defined_object_factory, eid_factory, get_response_object):
    admin_defined_object = admin_defined_object_factory()
    text_eid = eid_factory(type=EntityType.TEXT)
    chem_draw_eid = eid_factory(type=EntityType.CHEMICAL_DRAWING)
    unknown_eid = eid_factory(type='unknown')
    response_1 = {
        'links': {
            'self': f'https://example.com/{admin_defined_object.eid}/children?page[offset]=0&page[limit]=20',
            'next': f'https://example.com/{admin_defined_object.eid}/children?page[offset]=20&page[limit]=20',
        },
        'data': [
            {
                'type': ObjectType.ENTITY,
                'id': chem_draw_eid,
                'links': {'self': f'https://example.com/{chem_draw_eid}'},
                'attributes': {
                    'eid': chem_draw_eid,
                    'name': 'Some reactions',
                    'description': '',
                    'type': EntityType.CHEMICAL_DRAWING,
                    'createdAt': '2019-09-06T03:12:35.129Z',
                    'editedAt': '2019-09-06T15:22:47.309Z',
                    'digest': '123144',
                },
            },
            {
                'type': ObjectType.ENTITY,
                'id': unknown_eid,
                'links': {'self': f'https://example.com/{unknown_eid}'},
                'attributes': {
                    'eid': unknown_eid,
                    'name': 'Some reactions',
                    'description': '',
                    'type': 'unknown',
                    'createdAt': '2019-09-06T03:12:35.129Z',
                    'editedAt': '2019-09-06T15:22:47.309Z',
                    'digest': '123144',
                },
            },
        ],
    }
    response_2 = {
        'links': {
            'prev': f'https://example.com/{admin_defined_object.eid}/children?page[offset]=0&page[limit]=20',
            'self': f'https://example.com/{admin_defined_object.eid}/children?page[offset]=20&page[limit]=20',
        },
        'data': [
            {
                'type': ObjectType.ENTITY,
                'id': text_eid,
                'links': {'self': f'https://example.com/{text_eid}'},
                'attributes': {
                    'eid': text_eid,
                    'name': 'My text',
                    'description': '',
                    'type': EntityType.TEXT,
                    'createdAt': '2019-09-06T03:12:35.129Z',
                    'editedAt': '2019-09-06T15:22:47.309Z',
                    'digest': '123144',
                },
            },
        ],
    }

    api_mock.call.side_effect = [get_response_object(response_1), get_response_object(response_2)]

    result_generator = admin_defined_object.get_children()

    api_mock.call.assert_not_called()

    result = list(result_generator)

    api_mock.call.assert_has_calls(
        [
            mocker.call(
                method='GET',
                path=('entities', admin_defined_object.eid, 'children'),
                params={'order': 'layout'},
            ),
            mocker.call(
                method='GET',
                path=response_1['links']['next'],
            ),
        ]
    )

    assert isinstance(result[0], ChemicalDrawing)
    assert result[0].eid == chem_draw_eid

    assert isinstance(result[1], Entity)
    assert result[1].eid == unknown_eid

    assert isinstance(result[2], Text)
    assert result[2].eid == text_eid


def test_get_html(api_mock, admin_defined_object_factory, snapshot):
    admin_defined_object = admin_defined_object_factory(
        name='name',
        description='text',
        edited_at=datetime.datetime(2018, 6, 1, 1, 1, 1),
        children=[],
    )
    response = {
        'links': {'self': f'https://example.com/{admin_defined_object.eid}/children'},
        'data': [],
    }
    api_mock.call.return_value.json.return_value = response

    admin_defined_object_html = admin_defined_object.get_html()

    snapshot.assert_match(admin_defined_object_html)


def test_dump_templates(api_mock, mocker, admin_defined_object_factory, templates, get_response_object):
    admin_defined_object = admin_defined_object_factory(name='name')
    template_eid = templates['data'][0]['id']

    fs_handler_mock = mocker.MagicMock()
    base_path = './'
    metadata = {
        'eid': template_eid,
        'name': 'DEFAULT_admin_defined_object',
        'description': '',
    }

    api_mock.call.side_effect = [get_response_object(templates), get_response_object('')]
    admin_defined_object.dump_templates(base_path=base_path, fs_handler=fs_handler_mock)

    join_path_call_1 = mocker.call(base_path, 'templates', admin_defined_object.type)
    join_path_call_2 = mocker.call(fs_handler_mock.join_path(), template_eid, 'metadata.json')

    fs_handler_mock.join_path.assert_has_calls(
        [
            join_path_call_1,
            join_path_call_2,
        ],
        any_order=True,
    )
    fs_handler_mock.write.assert_has_calls(
        [
            mocker.call(fs_handler_mock.join_path(), json.dumps(metadata)),
        ],
        any_order=True,
    )
