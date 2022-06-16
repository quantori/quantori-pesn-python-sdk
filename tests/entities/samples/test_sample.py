import json

import arrow
import pytest

from signals_notebook.common_types import EntityType
from signals_notebook.entities import Sample, SampleProperty


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


def test_save(api_mock, sample_factory, sample_properties, mocker):
    sample = sample_factory()
    assert sample._properties == []

    api_mock.call.return_value.json.return_value = sample_properties
    created_properties = sample.properties

    assert sample._properties != []

    for item in created_properties:
        if item.id == '2':
            item.content.set_value('555')
    api_mock.call.return_value.json.return_value = {}
    api_mock.call.return_value.json.return_value = sample_properties

    request_body = []
    for item in created_properties:
        if item.is_changed:
            request_body.append(item.representation_for_update.dict(exclude_none=True))

    sample.save()

    api_mock.assert_has_calls(
        [
            mocker.call.call(
                method='GET',
                path=(sample._get_samples_endpoint(), sample.eid, 'properties'),
                params={
                    'name': None,
                    'value': 'normalized',
                },
            ),
            mocker.call.call(
                method='PATCH',
                path=(sample._get_samples_endpoint(), sample.eid, 'properties'),
                params={
                    'force': 'true',
                    'value': 'normalized',
                },
                json={
                    'data': {'attributes': {'data': request_body}},
                },
            ),
        ],
        any_order=True,
    )


@pytest.mark.parametrize('digest, force', [('111', False), (None, True)])
def test_create(api_mock, experiment_factory, sample_property_factory, sample_factory, eid_factory, digest, force):
    container = experiment_factory(digest=digest)
    sample_template = sample_factory()
    eid = eid_factory(type=EntityType.SAMPLE)
    response = {
        'links': {'self': 'https://example.com/sample:2d9c3f5c-065a-4d56-992f-c0b2003eb9be'},
        'data': {
            'type': 'entity',
            'id': eid,
            'attributes': {
                'id': eid,
                'eid': eid,
                'name': 'Sample-1781',
                'description': '',
                'createdAt': '2022-06-14T09:51:10.765Z',
                'editedAt': '2022-06-14T09:51:10.765Z',
                'type': 'sample',
                'digest': '25881025',
                'fields': {'Description': {'value': ''}, 'Name': {'value': 'Sample-1781'}},
                'flags': {'canEdit': True},
            },
        },
    }
    new_sample_property = sample_property_factory()
    request_body = {
        'data': {
            'type': 'sample',
            'attributes': {
                'fields': [
                    new_sample_property.dict(exclude_none=True),
                ]
            },
            'relationships': {
                'ancestors': {
                    'data': [
                        container.short_description.dict(exclude_none=True),
                    ]
                },
                'template': {'data': sample_template.short_description.dict(exclude_none=True)},
            },
        }
    }

    api_mock.call.return_value.json.return_value = response

    new_sample = Sample.create(
        properties=[new_sample_property], template=sample_template, ancestors=[container], digest=digest, force=force
    )

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('entities',),
        params={
            'digest': digest,
            'force': json.dumps(force),
        },
        json=request_body,
    )

    assert isinstance(new_sample, Sample)
    assert new_sample.eid == eid
    assert new_sample.digest == response['data']['attributes']['digest']
    assert new_sample.name == response['data']['attributes']['name']
    assert new_sample.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert new_sample.edited_at == arrow.get(response['data']['attributes']['editedAt'])
