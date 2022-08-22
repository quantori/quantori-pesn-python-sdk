import json

import arrow
import pytest

from signals_notebook.common_types import EID, EntityType, ObjectType
from signals_notebook.entities import Experiment
from signals_notebook.entities.notebook import Notebook


@pytest.fixture()
def templates():
    return {
        'links': {
            'self': 'https://ex.com/api/rest/v1.0/'
            'entities?includeTypes=journal&includeOptions=template&page[offset]=0&page[limit]=20',
            'first': 'https://ex.com/api/rest/v1.0/'
            'entities?includeTypes=journal&includeOptions=template&page[offset]=0&page[limit]=20',
        },
        'data': [
            {
                'type': 'entity',
                'id': 'journal:cbabfd5e-b6d3-4a0b-b8ca-fb4abe40ff6f',
                'links': {'self': 'https://ex.com/api/rest/v1.0/entities/journal:cbabfd5e-b6d3-4a0b-b8ca-fb4abe40ff6f'},
                'attributes': {
                    'id': 'journal:cbabfd5e-b6d3-4a0b-b8ca-fb4abe40ff6f',
                    'eid': 'journal:cbabfd5e-b6d3-4a0b-b8ca-fb4abe40ff6f',
                    'name': 'DEFAULT_NOTEBOOK',
                    'description': '',
                    'createdAt': '2021-10-22T13:36:01.989Z',
                    'editedAt': '2021-11-08T08:23:19.789Z',
                    'type': 'journal',
                    'digest': '95590489',
                    'fields': {
                        'Description': {'value': ''},
                        'My Notebook Field 1 (SK)': {'value': ''},
                        'My Notebook Field 2 (SK)': {'value': ''},
                        'Name': {'value': 'DEFAULT_NOTEBOOK'},
                    },
                    'flags': {'canEdit': True},
                },
            }
        ],
    }


@pytest.mark.parametrize('description', ['test description', None])
@pytest.mark.parametrize('digest, force', [('1234234', False), (None, True)])
def test_create(api_mock, description, digest, force):
    eid = EID('journal:e360eea6-b331-4c6f-b340-6d0eaa7eb070')
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'eid': eid,
                'name': 'My notebook',
                'description': description,
                'type': EntityType.NOTEBOOK,
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
            'type': EntityType.NOTEBOOK,
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


def test_get_children__one_page(api_mock, notebook_factory, eid_factory):
    notebook = notebook_factory()
    experiment_eid = eid_factory(type=EntityType.EXPERIMENT)

    response = {
        'links': {'self': f'https://example.com/{notebook.eid}/children'},
        'data': [
            {
                'type': ObjectType.ENTITY,
                'id': experiment_eid,
                'links': {'self': f'https://example.com/{experiment_eid}'},
                'attributes': {
                    'eid': experiment_eid,
                    'name': 'Experiment',
                    'description': '',
                    'type': EntityType.EXPERIMENT,
                    'createdAt': '2019-09-06T03:12:35.129Z',
                    'editedAt': '2019-09-06T15:22:47.309Z',
                    'digest': '123144',
                },
            },
        ],
    }
    api_mock.call.return_value.json.return_value = response

    result = list(notebook.get_children())

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', notebook.eid, 'children'),
        params={},
    )

    assert isinstance(result[0], Experiment)
    assert result[0].eid == experiment_eid


def test_dump_templates(api_mock, mocker, notebook_factory, templates, get_response_object):
    notebook = notebook_factory(name='name')
    template_eid = templates['data'][0]['id']

    fs_handler_mock = mocker.MagicMock()
    base_path = './'
    metadata = {
        'eid': template_eid,
        'name': 'DEFAULT_NOTEBOOK',
        'description': '',
    }

    api_mock.call.side_effect = [get_response_object(templates), get_response_object('')]
    notebook.dump_templates(base_path=base_path, fs_handler=fs_handler_mock)

    join_path_call_1 = mocker.call(base_path, 'templates', notebook.type)
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
