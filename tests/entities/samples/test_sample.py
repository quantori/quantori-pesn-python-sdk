import json
from uuid import UUID

import arrow
import pytest

from signals_notebook.common_types import EntityType
from signals_notebook.entities import Sample, SampleCell


def test_reload_properties(api_mock, sample_properties, sample_factory):
    sample = sample_factory()

    assert sample._cells == []

    api_mock.call.return_value.json.return_value = sample_properties

    for item in sample:
        assert isinstance(item, SampleCell)

    assert sample._cells != []

    api_mock.call.assert_called_once_with(
        method='GET',
        path=(sample._get_samples_endpoint(), sample.eid, 'properties'),
        params={
            'value': 'normalized',
        },
    )


def test_save(api_mock, sample_factory, sample_properties, mocker):
    sample = sample_factory()
    assert sample._cells == []

    api_mock.call.return_value.json.return_value = sample_properties

    for item in sample:
        if item.id == '2':
            item.set_content_value('555')
    api_mock.call.return_value.json.return_value = {}
    api_mock.call.return_value.json.return_value = sample_properties

    assert sample._cells != []

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
def test_create(api_mock, experiment_factory, sample_cell_factory, sample_factory, eid_factory, digest, force):
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
    new_sample_cell = sample_cell_factory()
    request_body = {
        'data': {
            'type': 'sample',
            'attributes': {
                'fields': [
                    new_sample_cell.dict(exclude_none=True, include={'id', 'name', 'content'}),
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
        cells=[new_sample_cell], template=sample_template, ancestors=[container], digest=digest, force=force
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


@pytest.mark.parametrize('index', [1, 'b718adec-73e0-3ce3-ac72-0dd11a06a308', 'digests.self'])
def test_getitem(api_mock, sample_properties, sample_factory, index):
    sample = sample_factory()

    assert sample._cells == []

    api_mock.call.return_value.json.return_value = sample_properties

    for item in sample:
        assert isinstance(item, SampleCell)

    assert isinstance(sample[index], SampleCell)

    assert sample._cells != []


def test_iter(api_mock, sample_properties, sample_factory):
    sample = sample_factory()

    assert sample._cells == []

    api_mock.call.return_value.json.return_value = sample_properties

    for item in sample:
        assert isinstance(item, SampleCell)

    assert sample._cells != []


def test_dump(api_mock, mocker, sample_factory, sample_properties):
    sample = sample_factory(name='name')

    fs_handler_mock = mocker.MagicMock()
    base_path = './'
    metadata = {
        'filename': f'{sample.name}.json',
        "columns": ["ID", "Template", None, None, "Created Date", "Description", "Comments"],
        **{k: v for k, v in sample.dict().items() if k in ('name', 'description', 'eid')},
    }

    api_mock.call.return_value.json.return_value = sample_properties
    sample.dump(base_path=base_path, fs_handler=fs_handler_mock)
    content = json.dumps({'data': [item.dict() for item in sample]}, default=str).encode('utf-8')

    join_path_call_1 = mocker.call(base_path, sample.eid, 'metadata.json')
    join_path_call_2 = mocker.call(base_path, sample.eid, f'{sample.name}.json')

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
            mocker.call(fs_handler_mock.join_path(), content),
        ],
        any_order=True,
    )


def test_dump_templates(api_mock, mocker, sample_factory, sample_properties, get_response_object, templates):
    sample = sample_factory(name='Sample')
    template_eid = templates['data'][0]['id']
    template_name = templates['data'][0]['attributes']['name']

    fs_handler_mock = mocker.MagicMock()
    base_path = './'
    metadata = {
        'filename': f'{sample.name}.json',
        "columns": ["ID", "Template", None, None, "Created Date", "Description", "Comments"],
        **{'eid': template_eid, 'name': template_name, 'description': ''},
    }

    api_mock.call.side_effect = [
        get_response_object(templates),
        get_response_object(sample_properties),
        get_response_object(sample_properties),
    ]
    sample.dump_templates(base_path=base_path, fs_handler=fs_handler_mock)

    content = json.dumps({'data': [item.dict() for item in sample]}, default=str).encode('utf-8')

    join_path_call_1 = mocker.call(base_path, 'templates', sample.type)
    join_path_call_2 = mocker.call(fs_handler_mock.join_path(), template_eid, 'metadata.json')
    join_path_call_3 = mocker.call(fs_handler_mock.join_path(), template_eid, f'{sample.name}.json')

    fs_handler_mock.join_path.assert_has_calls(
        [
            join_path_call_1,
            join_path_call_2,
            join_path_call_3,
        ],
        any_order=True,
    )
    fs_handler_mock.write.assert_has_calls(
        [
            mocker.call(fs_handler_mock.join_path(), json.dumps(metadata)),
            mocker.call(fs_handler_mock.join_path(), content),
        ],
        any_order=True,
    )
