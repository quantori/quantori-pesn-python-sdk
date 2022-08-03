import json
from uuid import UUID

import arrow
import pytest

from signals_notebook.common_types import EntityType, ObjectType
from signals_notebook.entities.parallel_experiment.parallel_experiment import ParallelExperiment
from signals_notebook.entities import ChemicalDrawing, Entity, Text, SubExperimentSummary

@pytest.fixture()
def get_response_experiment(mocker):
    def _f(response):
        mock = mocker.Mock()
        mock.json.return_value = response
        return mock

    return _f


@pytest.mark.parametrize('digest, force', [('111', False), (None, True)])
def test_create(api_mock, notebook_factory, eid_factory, digest, force):
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
                'type': EntityType.PARALLEL_EXPERIMENT,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '123144',
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = ParallelExperiment.create(name='My experiment', description='Some description', notebook=notebook)

    request_body = {
        'data': {
            'type': EntityType.PARALLEL_EXPERIMENT,
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

    assert isinstance(result, ParallelExperiment)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.description == response['data']['attributes']['description']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_get_children_one_page(api_mock, parallel_experiment_factory, eid_factory):
    experiment = parallel_experiment_factory()

    text_eid = eid_factory(type=EntityType.TEXT)
    chem_draw_eid = eid_factory(type=EntityType.CHEMICAL_DRAWING)
    subexp_sum_eid = eid_factory(type=EntityType.SUB_EXPERIMENT_SUMMARY)

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
                'id': subexp_sum_eid,
                'links': {'self': f'https://example.com/{subexp_sum_eid}'},
                'attributes': {
                    'eid': subexp_sum_eid,
                    'name': 'Some reactions',
                    'description': '',
                    'type': EntityType.SUB_EXPERIMENT_SUMMARY,
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

    assert isinstance(result[2], SubExperimentSummary)
    assert result[2].eid == subexp_sum_eid


def test_get_children_several_pages(mocker, api_mock, parallel_experiment_factory, eid_factory, get_response_experiment):
    experiment = parallel_experiment_factory()
    text_eid = eid_factory(type=EntityType.TEXT)
    chem_draw_eid = eid_factory(type=EntityType.CHEMICAL_DRAWING)
    subexp_sum_eid = eid_factory(type=EntityType.SUB_EXPERIMENT_SUMMARY)

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
                'id': subexp_sum_eid,
                'links': {'self': f'https://example.com/{subexp_sum_eid}'},
                'attributes': {
                    'eid': subexp_sum_eid,
                    'name': 'Some reactions',
                    'description': '',
                    'type': EntityType.SUB_EXPERIMENT_SUMMARY,
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

    assert isinstance(result[1], SubExperimentSummary)
    assert result[1].eid == subexp_sum_eid

    assert isinstance(result[2], Text)
    assert result[2].eid == text_eid


def test_get_html(api_mock, parallel_experiment_factory, snapshot):
    experiment = parallel_experiment_factory(
        name='name',
        description='text',
        children=[],
    )
    response = {
        'links': {'self': f'https://example.com/{experiment.eid}/children'},
        'data': [],
    }
    api_mock.call.return_value.json.return_value = response

    experiment_html = experiment.get_html()

    snapshot.assert_match(experiment_html)
