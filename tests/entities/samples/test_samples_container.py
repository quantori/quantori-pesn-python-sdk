import os

import pytest

from signals_notebook.common_types import File
from signals_notebook.entities.samples.sample import SampleProperty
from signals_notebook.entities.samples.sample_table_row import SampleTableRow


@pytest.fixture()
def samples_container_content():
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


def test_get_content(samples_container_factory, api_mock, samples_container_content):
    samples_container = samples_container_factory(name='name')
    file_name = 'Test.csv'
    content = samples_container_content
    content_type = 'text/csv'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    result = samples_container.get_content()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', samples_container.eid, 'export'),
        params={
            'format': None,
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type


def test_get_html(samples_container_factory, snapshot, api_mock, samples_container_content):
    samples_container = samples_container_factory(name='name')
    file_name = 'Test.csv'
    content = samples_container_content
    content_type = 'text/csv'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    samples_container_html = samples_container.get_html()

    snapshot.assert_match(samples_container_html)


def test_reload_samples_rows(api_mock, samples_container_factory, samples_from_table_response):
    samples_container = samples_container_factory()

    assert samples_container._samples_rows == []

    api_mock.call.return_value.json.return_value = samples_from_table_response
    created_sample_rows = samples_container.samples_rows

    assert samples_container._samples_rows != []
    assert isinstance(created_sample_rows[0], SampleTableRow)
    columns = created_sample_rows[0].columns

    for item in columns.values():
        assert isinstance(item, SampleProperty)

    assert len(columns) == 8

    api_mock.call.assert_called_once_with(
        method='GET',
        path=(samples_container._get_sample_tables_endpoint(), samples_container.eid, 'rows'),
        params={
            'sampleIds': None,
            'fields': '',
        },
    )


def test_fetch_samples_from_table(api_mock, samples_container_factory, samples_from_table_response):
    samples_container = samples_container_factory()
    api_mock.call.return_value.json.return_value = samples_from_table_response

    samples_generator = samples_container.fetch_samples_from_table()
    samples_table_row = list(samples_generator)[0]
    columns = samples_table_row.columns

    assert isinstance(samples_table_row, SampleTableRow)
    for item in columns.values():
        assert isinstance(item, SampleProperty)

    assert len(columns) == 8

    api_mock.call.assert_called_once_with(
        method='GET',
        path=(samples_container._get_sample_tables_endpoint(), samples_container.eid, 'rows'),
        params={
            'sampleIds': None,
            'fields': '',
        },
    )


def test_patch_sample_in_table(api_mock, samples_container_factory, samples_from_table_response, mocker):
    samples_container = samples_container_factory()

    assert samples_container._samples_rows == []

    api_mock.call.return_value.json.return_value = samples_from_table_response
    created_sample_rows = samples_container.samples_rows

    assert samples_container._samples_rows != []

    api_mock.call.return_value.json.return_value = {}
    api_mock.call.return_value.json.return_value = samples_from_table_response

    request_body = []
    for item in created_sample_rows:
        request_body.append(item.representation_for_update)

    samples_container.patch_sample_in_table()

    api_mock.assert_has_calls(
        [
            mocker.call.call(
                method='GET',
                path=(samples_container._get_sample_tables_endpoint(), samples_container.eid, 'rows'),
                params={
                    'sampleIds': None,
                    'fields': '',
                },
            ),
            mocker.call.call(
                method='PATCH',
                path=(samples_container._get_sample_tables_endpoint(), samples_container.eid, 'rows'),
                params={
                    'force': 'true',
                    'sampleIds': None,
                    'digest': None
                },
                json={
                    'data': request_body,
                },
            ),
        ],
        any_order=True,
    )
