import datetime

import arrow
import pytest

from signals_notebook.common_types import EntityType, ObjectType
from signals_notebook.entities import ChemicalDrawing, Entity, Experiment, Text


@pytest.fixture()
def get_response_experiment(mocker):
    def _f(response):
        mock = mocker.Mock()
        mock.json.return_value = response
        return mock

    return _f


@pytest.fixture()
def templates():
    return {
        'links': {
            'self': 'https://ex.com/api/rest/v1.0/'
            'entities?includeTypes=experiment&includeOptions=template&page[offset]=0&page[limit]=20',
            'first': 'https://ex.com/api/rest/v1.0/'
            'entities?includeTypes=experiment&includeOptions=template&page[offset]=0&page[limit]=20',
        },
        'data': [
            {
                'type': 'entity',
                'id': 'experiment:d4d25125-5665-4c89-b9b6-049b44e1355e',
                'links': {
                    'self': 'https://ex.com/api/rest/v1.0/entities/experiment:d4d25125-5665-4c89-b9b6-049b44e1355e'
                },
                'attributes': {
                    'id': 'experiment:d4d25125-5665-4c89-b9b6-049b44e1355e',
                    'eid': 'experiment:d4d25125-5665-4c89-b9b6-049b44e1355e',
                    'name': 'DEFAULT_EXPERIMENT',
                    'description': '',
                    'createdAt': '2021-10-22T13:36:01.730Z',
                    'editedAt': '2022-07-27T07:25:41.960Z',
                    'type': 'experiment',
                    'digest': '68929861',
                    'fields': {'Description': {'value': ''}, 'Name': {'value': 'DEFAULT_EXPERIMENT'}},
                    'flags': {'canEdit': True},
                },
            }
        ],
    }


@pytest.mark.parametrize('description', ['test description', None])
@pytest.mark.parametrize('digest, force', [('1234234', False), (None, True)])
def test_create(api_mock, description, digest, force, eid_factory):
    eid = eid_factory(type=EntityType.EXPERIMENT)
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'eid': eid,
                'name': 'My experiment',
                'description': description,
                'type': EntityType.EXPERIMENT,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': digest,
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = Experiment.create(name='My experiment', description=description, digest=digest, force=force)

    request_body = {
        'data': {
            'type': EntityType.EXPERIMENT,
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

    assert isinstance(result, Experiment)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.description == response['data']['attributes']['description']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_create_with_ancestors(api_mock, notebook_factory, eid_factory):
    notebook = notebook_factory()
    eid = eid_factory(type=EntityType.EXPERIMENT)
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'eid': eid,
                'name': 'My experiment',
                'description': 'Some description',
                'type': EntityType.EXPERIMENT,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '123144',
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = Experiment.create(name='My experiment', description='Some description', notebook=notebook, force=True)

    request_body = {
        'data': {
            'type': EntityType.EXPERIMENT,
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

    assert isinstance(result, Experiment)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.description == response['data']['attributes']['description']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_create_with_template(api_mock, experiment_factory, eid_factory):
    template = experiment_factory()
    eid = eid_factory(type=EntityType.EXPERIMENT)
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'eid': eid,
                'name': 'My experiment',
                'description': 'Some description',
                'type': EntityType.EXPERIMENT,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '123144',
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = Experiment.create(name='My experiment', description='Some description', template=template, force=True)

    request_body = {
        'data': {
            'type': EntityType.EXPERIMENT,
            'attributes': {
                'name': response['data']['attributes']['name'],
                'description': response['data']['attributes']['description'],
            },
            'relationships': {
                'template': {
                    'data': {
                        'id': template.eid,
                        'type': EntityType.EXPERIMENT,
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

    assert isinstance(result, Experiment)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.description == response['data']['attributes']['description']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


@pytest.mark.parametrize('force', [True, False])
def test_add_children(api_mock, experiment_factory, force, eid_factory):
    experiment = experiment_factory()
    eid = eid_factory(type=EntityType.EXPERIMENT)
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

    result = experiment.add_child(
        name='My text',
        content=b'Some text',
        content_type='text/plain',
        force=force,
    )

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('entities', experiment.eid, 'children', 'My text.txt'),
        params={
            'digest': None if force else experiment.digest,
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


def test_get_children__one_page(api_mock, experiment_factory, eid_factory):
    experiment = experiment_factory()
    text_eid = eid_factory(type=EntityType.TEXT)
    chem_draw_eid = eid_factory(type=EntityType.CHEMICAL_DRAWING)
    unknown_eid = eid_factory(type='unknown')
    response = {
        'links': {'self': f'https://example.com/{experiment.eid}/children'},
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

    result = list(experiment.get_children())

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', experiment.eid, 'children'),
        params={'order': 'layout'},
    )

    assert isinstance(result[0], Text)
    assert result[0].eid == text_eid

    assert isinstance(result[1], ChemicalDrawing)
    assert result[1].eid == chem_draw_eid

    assert isinstance(result[2], Entity)
    assert result[2].eid == unknown_eid


def test_get_children__several_pages(mocker, api_mock, experiment_factory, eid_factory, get_response_experiment):
    experiment = experiment_factory()
    text_eid = eid_factory(type=EntityType.TEXT)
    chem_draw_eid = eid_factory(type=EntityType.CHEMICAL_DRAWING)
    unknown_eid = eid_factory(type='unknown')
    response_1 = {
        'links': {
            'self': f'https://example.com/{experiment.eid}/children?page[offset]=0&page[limit]=20',
            'next': f'https://example.com/{experiment.eid}/children?page[offset]=20&page[limit]=20',
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
            'prev': f'https://example.com/{experiment.eid}/children?page[offset]=0&page[limit]=20',
            'self': f'https://example.com/{experiment.eid}/children?page[offset]=20&page[limit]=20',
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

    api_mock.call.side_effect = [get_response_experiment(response_1), get_response_experiment(response_2)]

    result_generator = experiment.get_children()

    api_mock.call.assert_not_called()

    result = list(result_generator)

    api_mock.call.assert_has_calls(
        [
            mocker.call(
                method='GET',
                path=('entities', experiment.eid, 'children'),
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


def test_get_html(api_mock, experiment_factory, snapshot):
    experiment = experiment_factory(
        name='name',
        description='text',
        edited_at=datetime.datetime(2018, 6, 1, 1, 1, 1),
        children=[],
    )
    response = {
        'links': {'self': f'https://example.com/{experiment.eid}/children'},
        'data': [],
    }
    api_mock.call.return_value.json.return_value = response

    experiment_html = experiment.get_html()

    snapshot.assert_match(experiment_html)
