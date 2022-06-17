import json
from uuid import UUID

import arrow
import pytest

from signals_notebook.common_types import EntityType
from signals_notebook.entities import Sample, SampleProperty


def test_reload_properties(api_mock, sample_properties, sample_factory):
    sample = sample_factory()

    assert sample._properties == []

    api_mock.call.return_value.json.return_value = sample_properties

    sample_property = sample[0]
    assert isinstance(sample_property, SampleProperty)

    for item in sample:
        assert isinstance(item, SampleProperty)

    assert sample._properties != []

    api_mock.call.assert_called_once_with(
        method='GET',
        path=(sample._get_samples_endpoint(), sample.eid, 'properties'),
        params={
            'value': 'normalized',
        },
    )


def test_save(api_mock, sample_factory, sample_properties, mocker):
    sample = sample_factory()
    assert sample._properties == []

    api_mock.call.return_value.json.return_value = sample_properties

    sample_property = sample[0]
    assert isinstance(sample_property, SampleProperty)

    for item in sample:
        if item.id == '2':
            item.set_content_value('555')
    api_mock.call.return_value.json.return_value = {}
    api_mock.call.return_value.json.return_value = sample_properties

    assert sample._properties != []

    request_body = []
    for item in sample:
        if item.is_changed:
            request_body.append(item.representation_for_update.dict(exclude_none=True))

    sample.save()

    api_mock.call.assert_has_calls(
        [
            mocker.call(
                method='GET',
                path=(sample._get_samples_endpoint(), sample.eid, 'properties'),
                params={
                    'value': 'normalized',
                },
            ),
            mocker.call(
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


@pytest.mark.parametrize(
    'index', [1, 'b718adec-73e0-3ce3-ac72-0dd11a06a308', 'digests.self', UUID('b718adec-73e0-3ce3-ac72-0dd11a06a308')]
)
def test_getitem(api_mock, sample_properties, sample_factory, index):
    sample = sample_factory()

    assert sample._properties == []

    api_mock.call.return_value.json.return_value = sample_properties

    sample_property = sample[0]
    assert isinstance(sample_property, SampleProperty)

    for item in sample:
        assert isinstance(item, SampleProperty)

    assert isinstance(sample[index], SampleProperty)

    assert sample._properties != []


def test_iter(api_mock, sample_properties, sample_factory):
    sample = sample_factory()

    assert sample._properties == []

    api_mock.call.return_value.json.return_value = sample_properties
    sample_property = sample[0]
    assert isinstance(sample_property, SampleProperty)

    for item in sample:
        assert isinstance(item, SampleProperty)

    assert sample._properties != []
