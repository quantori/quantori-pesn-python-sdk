import arrow
import pytest

from signals_notebook.entities import ChemicalDrawing, Entity, Experiment, Text
from signals_notebook.types import EID, EntitySubtype, EntityType


def test_get_list(api_mock):
    eid1 = EID('experiment:878a87ca-3777-4692-8561-a4a81ccfd85d')
    eid2 = EID('experiment:52062e1d-7e03-464f-8caf-d7ed93261213')
    response = {
        'links': {'self': f'https://example.com/{eid1}'},
        'data': [
            {
                'type': EntityType.ENTITY,
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
                'type': EntityType.ENTITY,
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

    result_generator = Experiment.get_list()

    api_mock.call.assert_not_called()

    result = list(result_generator)

    api_mock.call.assert_called_once_with(
        method='GET', path=('entities',), params={'includeTypes': EntitySubtype.EXPERIMENT}
    )

    for item, raw_item in zip(result, response['data']):
        assert isinstance(item, Experiment)
        assert item.eid == raw_item['id']
        assert item.digest == raw_item['attributes']['digest']
        assert item.name == raw_item['attributes']['name']
        assert item.description == raw_item['attributes']['description']
        assert item.created_at == arrow.get(raw_item['attributes']['createdAt'])
        assert item.edited_at == arrow.get(raw_item['attributes']['editedAt'])


@pytest.mark.parametrize('description', ['test description', None])
@pytest.mark.parametrize('digest, force', [('1234234', False), (None, True)])
def test_create(api_mock, description, digest, force):
    eid = EID('experiment:e360eea6-b331-4c6f-b340-6d0eaa7eb070')
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': EntityType.ENTITY,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'eid': eid,
                'name': 'My experiment',
                'description': description,
                'type': EntitySubtype.EXPERIMENT,
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
            'type': EntitySubtype.EXPERIMENT,
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


def test_create_with_ancestors(api_mock, notebook_factory):
    notebook = notebook_factory()
    eid = EID('experiment:e360eea6-b331-4c6f-b340-6d0eaa7eb070')
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': EntityType.ENTITY,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'eid': eid,
                'name': 'My experiment',
                'description': 'Some description',
                'type': EntitySubtype.EXPERIMENT,
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
            'type': EntitySubtype.EXPERIMENT,
            'attributes': {
                'name': response['data']['attributes']['name'],
                'description': response['data']['attributes']['description'],
            },
            'relationships': {
                'ancestors': {
                    'data': [
                        {
                            'id': notebook.eid,
                            'type': EntitySubtype.NOTEBOOK,
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


def test_create_with_template(api_mock, experiment_factory):
    template = experiment_factory()
    eid = EID('experiment:e360eea6-b331-4c6f-b340-6d0eaa7eb070')
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': EntityType.ENTITY,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'eid': eid,
                'name': 'My experiment',
                'description': 'Some description',
                'type': EntitySubtype.EXPERIMENT,
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
            'type': EntitySubtype.EXPERIMENT,
            'attributes': {
                'name': response['data']['attributes']['name'],
                'description': response['data']['attributes']['description'],
            },
            'relationships': {
                'template': {
                    'data': {
                        'id': template.eid,
                        'type': EntitySubtype.EXPERIMENT,
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


def test_delete_instance(experiment_factory, api_mock):
    experiment = experiment_factory()

    experiment.delete()

    api_mock.call.assert_called_once_with(
        method='DELETE',
        path=('entities', experiment.eid),
        params={
            'digest': None,
            'force': 'true',
        },
    )


@pytest.mark.parametrize('force', [True, False])
def test_update(api_mock, experiment_factory, force):
    experiment = experiment_factory()

    experiment.name = 'My experiment'
    experiment.description = 'New description'
    experiment.save(force=force)

    api_mock.call.assert_called_once_with(
        method='PATCH',
        path=('entities', experiment.eid, 'properties'),
        params={
            'digest': None if force else experiment.digest,
            'force': 'true' if force else 'false',
        },
        json={
            'data': [
                {'attributes': {'name': 'Name', 'value': 'My experiment'}},
                {'attributes': {'name': 'Description', 'value': 'New description'}},
            ]
        },
    )


@pytest.mark.parametrize('force', [True, False])
def test_add_children(api_mock, experiment_factory, force):
    experiment = experiment_factory()
    eid = EID('experiment:e360eea6-b331-4c6f-b340-6d0eaa7eb070')
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': EntityType.ENTITY,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'eid': eid,
                'name': 'My text',
                'description': '',
                'type': EntitySubtype.TEXT,
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


def test_get_children(api_mock, experiment_factory):
    experiment = experiment_factory()
    response = {
        'links': {'self': f'https://example.com/{experiment.eid}/children'},
        'data': [
            {
                'type': EntityType.ENTITY,
                'id': 'text:ce0b5848-6256-4eb9-9e90-3dfaefc0e53d',
                'links': {'self': f'https://example.com/text:ce0b5848-6256-4eb9-9e90-3dfaefc0e53d'},
                'attributes': {
                    'eid': 'text:ce0b5848-6256-4eb9-9e90-3dfaefc0e53d',
                    'name': 'My text',
                    'description': '',
                    'type': EntitySubtype.TEXT,
                    'createdAt': '2019-09-06T03:12:35.129Z',
                    'editedAt': '2019-09-06T15:22:47.309Z',
                    'digest': '123144',
                },
            },
            {
                'type': EntityType.ENTITY,
                'id': 'chemicalDrawing:2a632ec6-e8a0-4dcd-ac8a-75327654b4c3',
                'links': {'self': f'https://example.com/chemicalDrawing:2a632ec6-e8a0-4dcd-ac8a-75327654b4c3'},
                'attributes': {
                    'eid': 'chemicalDrawing:2a632ec6-e8a0-4dcd-ac8a-75327654b4c3',
                    'name': 'Some reactions',
                    'description': '',
                    'type': EntitySubtype.CHEMICAL_DRAWING,
                    'createdAt': '2019-09-06T03:12:35.129Z',
                    'editedAt': '2019-09-06T15:22:47.309Z',
                    'digest': '123144',
                },
            },
            {
                'type': EntityType.ENTITY,
                'id': 'unknown:d25eeb3a-ff62-47b8-ab43-e0f89ec8799d',
                'links': {'self': f'https://example.com/unknown:d25eeb3a-ff62-47b8-ab43-e0f89ec8799d'},
                'attributes': {
                    'eid': 'unknown:d25eeb3a-ff62-47b8-ab43-e0f89ec8799d',
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
    assert result[0].eid == 'text:ce0b5848-6256-4eb9-9e90-3dfaefc0e53d'

    assert isinstance(result[1], ChemicalDrawing)
    assert result[1].eid == 'chemicalDrawing:2a632ec6-e8a0-4dcd-ac8a-75327654b4c3'

    assert isinstance(result[2], Entity)
    assert result[2].eid == 'unknown:d25eeb3a-ff62-47b8-ab43-e0f89ec8799d'
