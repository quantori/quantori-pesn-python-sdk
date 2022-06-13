import arrow
import pytest

from signals_notebook.common_types import EntityType
from signals_notebook.entities import Sample
from signals_notebook.entities.samples.sample import SampleProperty


@pytest.fixture()
def sample_properties():
    return {
        'links': {'self': 'https://example.com/samples/properties'},
        'data': [
            {
                'type': 'property',
                'id': 'b718adec-73e0-3ce3-ac72-0dd11a06a308',
                'attributes': {
                    'id': 'b718adec-73e0-3ce3-ac72-0dd11a06a308',
                    'name': 'ID',
                    'content': {'value': 'Sample-1756'},
                },
            },
            {
                'type': 'property',
                'id': '278c491b-dd8a-3361-8c14-9c4ac790da34',
                'attributes': {
                    'id': '278c491b-dd8a-3361-8c14-9c4ac790da34',
                    'name': 'Template',
                    'content': {'value': 'Sample'},
                },
            },
            {
                'type': 'property',
                'id': 'digests.self',
                'attributes': {'id': 'digests.self'},
            },
            {
                'type': 'property',
                'id': 'digests.external',
                'attributes': {'id': 'digests.external'},
            },
            {
                'type': 'property',
                'id': '1',
                'attributes': {
                    'id': '1',
                    'name': 'Created Date',
                    'content': {'value': '2022-06-02T07:27:10.072365283Z'},
                },
            },
            {
                'type': 'property',
                'id': '2',
                'attributes': {'id': '2', 'name': 'Description', 'content': {'value': 'simple'}},
            },
            {
                'type': 'property',
                'id': '3',
                'attributes': {'id': '3', 'name': 'Comments', 'content': {'value': '555'}},
            },
        ],
    }


def test_get_properties(api_mock, sample_factory, sample_properties):
    sample = sample_factory()
    api_mock.call.return_value.json.return_value = sample_properties

    properties_generator = sample.get_properties()
    properties = list(properties_generator)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=(sample._get_samples_endpoint(), sample.eid, 'properties'),
        params={
            'name': None,
            'value': 'normalized',
        },
    )
    for item in properties:
        assert isinstance(item, SampleProperty)

    assert len(properties) == 7


def test_reload_properties(api_mock, sample_properties, sample_factory):
    sample = sample_factory()

    assert sample._properties == []

    api_mock.call.return_value.json.return_value = sample_properties
    created_properties = sample.properties

    assert sample._properties != []

    assert len(created_properties) == 7
    for item in created_properties:
        assert isinstance(item, SampleProperty)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=(sample._get_samples_endpoint(), sample.eid, 'properties'),
        params={
            'name': None,
            'value': 'normalized',
        },
    )


@pytest.mark.parametrize(
    'property_id, name, value', [('1', 'ID', 'SAMPLE-1'), ('2', 'SMTH', 'F1'), ('3', 'SMTH-ELSE', 'INDYCAR')]
)
def test_get_property_by_id(api_mock, sample_factory, property_id, name, value):
    sample = sample_factory()
    api_mock.call.return_value.json.return_value = {
        'data': {
            'type': 'property',
            'id': property_id,
            'attributes': {
                'id': property_id,
                'name': name,
                'content': {'value': value},
            },
        },
    }
    sample_property = sample.get_property_by_id(property_id)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=(sample._get_samples_endpoint(), sample.eid, 'properties', property_id),
        params={
            'value': 'normalized',
        },
    )

    assert isinstance(sample_property, SampleProperty)
    assert sample_property.id == property_id
    assert sample_property.name == name
    assert sample_property.content.value == value


def test_save(sample_factory):
    pass


@pytest.mark.skip()
@pytest.mark.parametrize('digest, force', [('111', False), (None, True)])
def test_create(api_mock, experiment_factory, eid_factory, digest, force):
    container = experiment_factory(digest=digest)
    eid = eid_factory(type=EntityType.SAMPLE)
    response = {}

    api_mock.call.return_value.json.return_value = response

    result = Sample.create(container=container)

    # api_mock.call.assert_called_once_with(
    #     method='POST',
    #     path=('entities', container.eid, 'children', ...),
    #     params={
    #         'digest': container.digest,
    #         'force': 'true' if force else 'false',
    #     },
    #     # headers={
    #     #     'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    #     # },
    #     # data=content.encode('utf-8'),
    # )

    assert isinstance(result, Sample)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])
