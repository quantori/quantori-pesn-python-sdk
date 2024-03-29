import datetime
import json

import arrow
import pytest

from signals_notebook.common_types import EntityType, ObjectType
from signals_notebook.entities import ChemicalDrawing, Text
from signals_notebook.entities.parallel_experiment.sub_experiment import SubExperiment


@pytest.fixture()
def get_response_experiment(mocker):
    def _f(response):
        mock = mocker.Mock()
        mock.json.return_value = response
        return mock

    return _f


@pytest.mark.parametrize('digest, force', [('111', False), (None, True)])
def test_create(api_mock, parallel_experiment_factory, eid_factory, digest, force):
    parallel_experiment = parallel_experiment_factory()
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
                'type': EntityType.SUB_EXPERIMENT,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '123144',
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = SubExperiment.create(description='Some description', parallel_experiment=parallel_experiment)

    request_body = {
        'data': {
            'type': EntityType.SUB_EXPERIMENT,
            'attributes': {'description': response['data']['attributes']['description']},
            'relationships': {
                'ancestors': {
                    'data': [
                        {
                            'id': parallel_experiment.eid,
                            'type': EntityType.PARALLEL_EXPERIMENT,
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

    assert isinstance(result, SubExperiment)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.description == response['data']['attributes']['description']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_get_children_one_page(api_mock, sub_experiment_factory, eid_factory):
    experiment = sub_experiment_factory()

    text_eid = eid_factory(type=EntityType.TEXT)
    chem_draw_eid = eid_factory(type=EntityType.CHEMICAL_DRAWING)

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
        ],
    }
    api_mock.call.return_value.json.return_value = response

    result = list(experiment.get_children())

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', experiment.eid, 'children'),
        params={},
    )

    assert isinstance(result[0], Text)
    assert result[0].eid == text_eid

    assert isinstance(result[1], ChemicalDrawing)
    assert result[1].eid == chem_draw_eid


def test_get_children_several_pages(mocker, api_mock, sub_experiment_factory, eid_factory, get_response_experiment):
    experiment = sub_experiment_factory()
    text_eid = eid_factory(type=EntityType.TEXT)
    chem_draw_eid = eid_factory(type=EntityType.CHEMICAL_DRAWING)

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
                params={},
            ),
            mocker.call(
                method='GET',
                path=response_1['links']['next'],
            ),
        ]
    )

    assert isinstance(result[0], ChemicalDrawing)
    assert result[0].eid == chem_draw_eid

    assert isinstance(result[1], Text)
    assert result[1].eid == text_eid


def test_get_html(api_mock, sub_experiment_factory, snapshot):
    experiment = sub_experiment_factory(
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


def test_load(
    api_mock, parallel_experiment_factory, chemical_drawing_factory, eid_factory, mocker, get_response_experiment
):
    chemical_drawing = chemical_drawing_factory(name='name')
    container = parallel_experiment_factory()
    eid = eid_factory(type=EntityType.PARALLEL_EXPERIMENT)

    fs_handler_mock = mocker.MagicMock()
    base_path = './'
    metadata = {
        'base_type': 'experiment',
        'eid': eid,
        'name': 'Sub_exp',
        'description': '',
    }
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'links': {'self': f'https://example.com/{eid}'},
            'attributes': {
                'eid': eid,
                'name': 'Par_exp',
                'description': '',
                'type': EntityType.SUB_EXPERIMENT,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '123144',
            },
        },
    }
    children_response = {
        'links': {'self': f'https://example.com/{eid}/children'},
        'data': [
            {
                'type': ObjectType.ENTITY,
                'id': chemical_drawing.eid,
                'links': {'self': f'https://example.com/{chemical_drawing.eid}'},
                'attributes': {
                    'eid': chemical_drawing.eid,
                    'name': 'Chemical Drawing',
                    'description': '',
                    'type': EntityType.CHEMICAL_DRAWING,
                    'createdAt': '2019-09-06T03:12:35.129Z',
                    'editedAt': '2019-09-06T15:22:47.309Z',
                    'digest': '123144',
                },
            },
        ],
    }
    api_mock.call.side_effect = [get_response_experiment(response), get_response_experiment(children_response)]
    fs_handler_mock.read.side_effect = [json.dumps(metadata)]
    fs_handler_mock.join_path.side_effect = [base_path + 'metadata.json']

    SubExperiment.load(path=base_path, fs_handler=fs_handler_mock, parallel_experiment=container)

    fs_handler_mock.join_path.assert_called_once_with(base_path, 'metadata.json')

    fs_handler_mock.read.assert_called_once_with(base_path + 'metadata.json')

    request_body = {
        'data': {
            'type': EntityType.SUB_EXPERIMENT,
            'attributes': {
                'description': response['data']['attributes']['description'],
            },
            'relationships': {
                'ancestors': {
                    'data': [
                        {
                            'type': EntityType.PARALLEL_EXPERIMENT,
                            'id': container.eid,
                        }
                    ]
                }
            },
        }
    }
    api_mock.call.assert_has_calls(
        [
            mocker.call(
                method='POST',
                path=('entities',),
                params={
                    'digest': None,
                    'force': 'true',
                },
                json=request_body,
            ),
            mocker.call(
                method='GET',
                path=('entities', eid, 'children'),
                params={},
            ),
        ]
    )
