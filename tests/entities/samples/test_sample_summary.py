import os

import pytest

from signals_notebook.common_types import File
from signals_notebook.entities.samples.sample import Sample, SampleProperty
from signals_notebook.entities.samples.sample_table_row import SampleTableRow


@pytest.fixture()
def samples_from_summary_response():
    return {
        'data': [
            {
                'type': 'entity',
                'id': 'sample:0f96db87-a4af-46ae-9aff-711867f23d73',
                'attributes': {
                    'id': 'sample:0f96db87-a4af-46ae-9aff-711867f23d73',
                    'eid': 'sample:0f96db87-a4af-46ae-9aff-711867f23d73',
                    'name': 'Sample-1764',
                    'description': '',
                    'createdAt': '2022-06-06T08:54:51.624Z',
                    'editedAt': '2022-06-06T08:54:51.624Z',
                    'type': 'sample',
                    'digest': '82858260',
                    'fields': {
                        'Amount': {'display': '1 g', 'value': '1', 'units': 'g'},
                        'Attached Docs': {'value': '0', 'eid': 'sample:0f96db87-a4af-46ae-9aff-711867f23d73'},
                        'Comments': {'value': 'Comments 1'},
                        'Created Date': {'value': '2022-06-06T08:54:51.677884071Z'},
                        'Description': {'value': 'Description 1'},
                        'ID': {
                            'type': 'sample',
                            'display': 'Sample-1764',
                            'value': 'sample:0f96db87-a4af-46ae-9aff-711867f23d73',
                        },
                        'Name': {
                            'type': 'parasubexp',
                            'display': 'Sub-experiment-1',
                            'value': 'parasubexp:413779cf-16b9-49ce-bb85-85b2fa6964da',
                        },
                        'Template': {'value': 'Sample'},
                    },
                },
            },
            {
                'type': 'entity',
                'id': 'sample:ba804b7d-f61c-4a8b-b2f9-4be4652b6286',
                'attributes': {
                    'id': 'sample:ba804b7d-f61c-4a8b-b2f9-4be4652b6286',
                    'eid': 'sample:ba804b7d-f61c-4a8b-b2f9-4be4652b6286',
                    'name': 'Sample-1774',
                    'description': '',
                    'createdAt': '2022-06-08T10:35:27.253Z',
                    'editedAt': '2022-06-08T10:35:27.253Z',
                    'type': 'sample',
                    'digest': '47537404',
                    'fields': {
                        'Attached Docs': {'value': '0', 'eid': 'sample:ba804b7d-f61c-4a8b-b2f9-4be4652b6286'},
                        'Created Date': {'value': '2022-06-08T10:35:27.346810619Z'},
                        'ID': {
                            'type': 'sample',
                            'display': 'Sample-1774',
                            'value': 'sample:ba804b7d-f61c-4a8b-b2f9-4be4652b6286',
                        },
                        'Name': {
                            'type': 'parasubexp',
                            'display': 'Sub-experiment-3',
                            'value': 'parasubexp:797df7e4-81b1-43b5-93b1-933f2b6082a5',
                        },
                        'Template': {'value': 'Sample'},
                    },
                },
            },
        ],
    }


@pytest.fixture()
def sample_summary_content():
    return (
        b'Name,ID,Created Date,Description,Comments,Amount,Attached Docs,Template'
        + os.linesep.encode('utf-8')
        + b'Sub-experiment-1,Sample-1764,2022-06-06T08:54:51.677884071Z,Description 1,Comments 1,1 g,0,Sample'
        + os.linesep.encode('utf-8')
        + b'Sub-experiment-3,Sample-1774,2022-06-08T10:35:27.346810619Z,,,,0,Sample'
    )


def test_create(sample_summary_factory):
    pass


def test_fetch_samples_from_summary(api_mock, sample_summary_factory, samples_from_summary_response):
    sample_summary = sample_summary_factory()
    api_mock.call.return_value.json.return_value = samples_from_summary_response

    samples_generator = sample_summary.fetch_samples_from_summary()
    samples = list(samples_generator)

    for item in samples:
        assert isinstance(item, Sample)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=(sample_summary._get_sample_summary_endpoint(), sample_summary.eid, 'samples'),
    )


def test_fetch_samples_from_table(api_mock, sample_summary_factory, samples_from_table_response):
    sample_summary = sample_summary_factory()
    api_mock.call.return_value.json.return_value = samples_from_table_response

    samples_generator = sample_summary.fetch_samples_from_table()
    samples_table_row = list(samples_generator)[0]
    columns = samples_table_row.columns

    assert isinstance(samples_table_row, SampleTableRow)
    for item in columns.values():
        assert isinstance(item, SampleProperty)

    assert len(columns) == 8

    api_mock.call.assert_called_once_with(
        method='GET',
        path=(sample_summary._get_sample_tables_endpoint(), sample_summary.eid, 'rows'),
        params={
            'sampleIds': None,
            'fields': '',
        },
    )


def test_patch_sample_in_table(sample_summary_factory):
    pass


def test_reload_samples_rows(api_mock, sample_summary_factory, samples_from_table_response):
    sample_summary = sample_summary_factory()

    assert sample_summary._samples_rows == []

    api_mock.call.return_value.json.return_value = samples_from_table_response
    created_sample_rows = sample_summary.samples_rows

    assert sample_summary._samples_rows != []
    assert isinstance(created_sample_rows[0], SampleTableRow)
    columns = created_sample_rows[0].columns

    for item in columns.values():
        assert isinstance(item, SampleProperty)

    assert len(columns) == 8

    api_mock.call.assert_called_once_with(
        method='GET',
        path=(sample_summary._get_sample_tables_endpoint(), sample_summary.eid, 'rows'),
        params={
            'sampleIds': None,
            'fields': '',
        },
    )


def test_get_content(api_mock, sample_summary_factory, sample_summary_content):
    sample_summary = sample_summary_factory()
    file_name = 'Test.csv'
    content_type = 'text/csv'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = sample_summary_content

    result = sample_summary.get_content()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', sample_summary.eid, 'export'),
        params={
            'format': None,
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == sample_summary_content
    assert result.content_type == content_type


def test_get_html(sample_summary_factory, snapshot, api_mock, sample_summary_content):
    sample_summary = sample_summary_factory(name='name')
    file_name = 'Test.csv'
    content = sample_summary_content
    content_type = 'text/csv'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    sample_summary_html = sample_summary.get_html()
    snapshot.assert_match(sample_summary_html)
