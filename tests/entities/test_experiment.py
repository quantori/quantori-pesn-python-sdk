import arrow
import pytest

from signals_notebook.entities import ChemicalDrawing, Entity, Experiment, Text
from signals_notebook.common_types import EntityType, ObjectType


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


def test_get_children(api_mock, experiment_factory, eid_factory):
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

    result = experiment.get_children()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', experiment.eid, 'children'),
    )

    assert isinstance(result[0], Text)
    assert result[0].eid == text_eid

    assert isinstance(result[1], ChemicalDrawing)
    assert result[1].eid == chem_draw_eid

    assert isinstance(result[2], Entity)
    assert result[2].eid == unknown_eid
