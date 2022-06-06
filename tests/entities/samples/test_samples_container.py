import pytest

from signals_notebook.common_types import File, EntityType


@pytest.fixture()
def samples_container_content():
    return (
        b'ID,Created Date,Description,Comments,Amount,Attached Docs,Template,Chemical Name,FM,EM,MF,MW'
        b'Sample-1756,2022-06-02T07:27:10.072365283Z,,,,0,Sample,,,,,'
        b'Sample-1757,2022-06-02T08:00:04.957872846Z,,,,0,Chemical Sample,HCl,36.46 g/mol,35.97668,ClH,36.46 g/mol'
        b'Sample-1758,2022-06-02T08:00:25.418330849Z,,,,0,Chemical Sample,H2O,18.02 g/mol,18.01056,H2O,18.02 g/mol'
        b'Sample-1759,2022-06-02T10:37:06.717628796Z,hh,,,0,Sample,,,,,'
        b'Sample-1760,2022-06-02T10:37:06.718687326Z,hh,,,0,Sample,,,,,'
    )


@pytest.mark.parametrize('digest, force', [('111', False), (None, True)])
def test_create(api_mock, experiment_factory, eid_factory, samples_container_content, digest, force):
    container = experiment_factory(digest=digest)
    eid = eid_factory(type=EntityType.SAMPLES_CONTAINER)
    file_name = 'Test.csv'
    content = samples_container_content
    content_type = 'text/csv'


def test_get_content(samples_container_factory, api_mock, samples_container_content):
    samples_container = samples_container_factory(name='name')
    file_name = 'Test.csv'
    content = samples_container_content
    content_type = 'text/csv'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}'
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
