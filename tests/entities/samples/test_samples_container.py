import os

import pytest

from signals_notebook.common_types import EID, File, SamplesContainerFormat
from signals_notebook.entities.samples.sample import Sample, SampleCell


@pytest.fixture()
def get_samples_response():
    return {
        'links': {
            'self': 'https://example.com/entities/samplesContainer',
        },
        'data': [
            {
                'type': 'entity',
                'id': 'sample:fa34c835-6271-4c59-b320-ff26089e89c6',
                'attributes': {
                    'id': 'sample:fa34c835-6271-4c59-b320-ff26089e89c6',
                    'eid': 'sample:fa34c835-6271-4c59-b320-ff26089e89c6',
                    'name': 'Sample-1776',
                    'description': '',
                    'createdAt': '2022-06-13T13:54:43.040Z',
                    'editedAt': '2022-06-15T12:20:52.715Z',
                    'type': 'sample',
                    'digest': '58181453',
                    'fields': {'Description': {'value': ''}, 'Name': {'value': 'Sample-1776'}},
                    'flags': {'canEdit': True},
                },
            },
            {
                'type': 'entity',
                'id': 'sample:ef8f39e5-3309-4f85-abd6-3ceedce0d8a6',
                'attributes': {
                    'id': 'sample:ef8f39e5-3309-4f85-abd6-3ceedce0d8a6',
                    'eid': 'sample:ef8f39e5-3309-4f85-abd6-3ceedce0d8a6',
                    'name': 'Sample-1777',
                    'description': '',
                    'createdAt': '2022-06-13T13:55:51.150Z',
                    'editedAt': '2022-06-14T10:46:52.907Z',
                    'type': 'sample',
                    'digest': '78660064',
                    'fields': {'Description': {'value': ''}, 'Name': {'value': 'Sample-1777'}},
                    'flags': {'canEdit': True},
                },
            },
            {
                'type': 'entity',
                'id': 'sample:3ef80703-612e-465a-b930-f3e154dd1937',
                'attributes': {
                    'id': 'sample:3ef80703-612e-465a-b930-f3e154dd1937',
                    'eid': 'sample:3ef80703-612e-465a-b930-f3e154dd1937',
                    'name': 'Sample-1778',
                    'description': '',
                    'createdAt': '2022-06-13T13:59:34.447Z',
                    'editedAt': '2022-06-13T13:59:34.447Z',
                    'type': 'sample',
                    'digest': '18903856',
                    'fields': {'Description': {'value': ''}, 'Name': {'value': 'Sample-1778'}},
                    'flags': {'canEdit': True},
                },
            },
        ],
    }


@pytest.fixture()
def samples_container_csv_content():
    return (
        b'ID,Created Date,Description,Comments,Amount,Attached Docs,Template,Chemical Name,FM,EM,MF,MW'
        + os.linesep.encode('utf-8')
        + b'Sample-1756,2022-06-02T07:27:10.072365283Z,,,,0,Sample,,,,,'
        + os.linesep.encode('utf-8')
        + b'Sample-1757,2022-06-02T08:00:04.957872846Z,,,,0,Chemical Sample,HCl,36.46 g/mol,35.97668,ClH,36.46 g/mol'
        + os.linesep.encode('utf-8')
        + b'Sample-1758,2022-06-02T08:00:25.418330849Z,,,,0,Chemical Sample,H2O,18.02 g/mol,18.01056,H2O,18.02 g/mol'
        + os.linesep.encode('utf-8')
        + b'Sample-1759,2022-06-02T10:37:06.717628796Z,hh,,,0,Sample,,,,,'
        + os.linesep.encode('utf-8')
        + b'Sample-1760,2022-06-02T10:37:06.718687326Z,hh,,,0,Sample,,,,,'
    )


@pytest.fixture()
def samples_container_sdf_content():
    path = os.path.join(os.path.dirname(__file__), 'samples_container_sdf_data.sdf')
    with open(path) as sdf_file:
        file = File(sdf_file)
        return file.content


@pytest.mark.parametrize(
    'file_name, content_type, format',
    [
        ('Test.csv', 'text/csv', SamplesContainerFormat.CSV),
        ('Test.sdf', 'chemical/x-mdl-sdfile', SamplesContainerFormat.SDF),
    ],
)
def test_get_content(
    samples_container_factory,
    api_mock,
    file_name,
    content_type,
    format,
    samples_container_csv_content,
    samples_container_sdf_content,
):
    samples_container = samples_container_factory(name='name')

    content = samples_container_csv_content if format == SamplesContainerFormat.CSV else samples_container_sdf_content

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    result = samples_container.get_content(format=format)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', samples_container.eid, 'export'),
        params={
            'format': format,
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type


def test_get_html(samples_container_factory, snapshot, api_mock, samples_container_csv_content):
    samples_container = samples_container_factory(name='name')
    file_name = 'Test.csv'
    content = samples_container_csv_content
    content_type = 'text/csv'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    samples_container_html = samples_container.get_html()

    snapshot.assert_match(samples_container_html)


def test_reload_samples(api_mock, samples_container_factory, get_samples_response, mocker, sample_properties):
    samples_container = samples_container_factory()

    assert samples_container._samples == []

    api_mock.call.return_value.json.return_value = get_samples_response

    samples_ids = [item['id'] for item in get_samples_response['data']]

    for sample in samples_container:
        assert isinstance(sample, Sample)
        api_mock.call.return_value.json.return_value = sample_properties
        sample_property = sample[0]
        assert isinstance(sample_property, SampleCell)

        for item in sample:
            assert isinstance(item, SampleCell)

    assert samples_container._samples != []

    api_mock.assert_has_calls(
        [
            mocker.call.call(
                method='GET',
                path=('samples', item, 'properties'),
                params={
                    'value': 'normalized',
                },
            )
            for item in samples_ids
        ],
        any_order=True,
    )


def test_save(api_mock, samples_container_factory, get_samples_response, sample_properties, mocker):
    samples_container = samples_container_factory()

    assert samples_container._samples == []

    api_mock.call.return_value.json.return_value = get_samples_response

    samples_ids = [item['id'] for item in get_samples_response['data']]

    patch_calls = []
    for sample in samples_container:

        request_body = []
        api_mock.call.return_value.json.return_value = sample_properties
        sample_property = sample[0]
        assert isinstance(sample_property, SampleCell)

        for item in sample:
            if item.id == '2':
                item.content.set_value('555')
        api_mock.call.return_value.json.return_value = {}
        api_mock.call.return_value.json.return_value = sample_properties

        for item in sample:
            if item.is_changed:
                request_body.append(item.representation_for_update.dict(exclude_none=True))

        patch_calls.append(
            mocker.call(
                method='PATCH',
                path=('samples', sample.eid, 'properties'),
                params={
                    'force': 'true',
                    'value': 'normalized',
                },
                json={
                    'data': {'attributes': {'data': request_body}},
                },
            )
        )

    assert samples_container._samples != []

    api_mock.call.return_value.json.return_value = get_samples_response
    samples_container.save()

    get_calls = [
        mocker.call(
            method='GET',
            path=('samples', item, 'properties'),
            params={
                'value': 'normalized',
            },
        )
        for item in samples_ids
    ]
    api_mock.call.assert_has_calls(
        [
            *patch_calls,
            *get_calls,
            mocker.call(
                method='GET',
                path=('entities', samples_container.eid, 'children'),
            ),
        ],
        any_order=True,
    )


@pytest.mark.parametrize(
    'index', [1, 'sample:fa34c835-6271-4c59-b320-ff26089e89c6', EID('sample:fa34c835-6271-4c59-b320-ff26089e89c6')]
)
def test_getitem(api_mock, samples_container_factory, get_samples_response, index):
    samples_container = samples_container_factory()

    assert samples_container._samples == []

    api_mock.call.return_value.json.return_value = get_samples_response
    sample = samples_container[0]
    assert isinstance(sample, Sample)

    assert samples_container._samples != []

    assert isinstance(samples_container[index], Sample)


def test_iter(api_mock, samples_container_factory, get_samples_response, sample_properties):
    samples_container = samples_container_factory()

    assert samples_container._samples == []

    api_mock.call.return_value.json.return_value = get_samples_response

    for sample in samples_container:
        assert isinstance(sample, Sample)

        api_mock.call.return_value.json.return_value = sample_properties
        sample_property = sample[0]
        assert isinstance(sample_property, SampleCell)

        for item in sample:
            assert isinstance(item, SampleCell)

    assert samples_container._samples != []
