import arrow
import pytest

from signals_notebook.common_types import EntityType, File, ObjectType
from signals_notebook.entities import BiologicalSequence


@pytest.fixture
def bio_seq_content():
    with open('tests/entities/test_files/bio_sequence_content.gb') as bio_seq_file:
        file = File(bio_seq_file)
        return file.content


@pytest.mark.parametrize('digest, force', [('111', False), (None, True)])
def test_create(api_mock, experiment_factory, eid_factory, digest, force, bio_seq_content):
    container = experiment_factory(digest=digest)
    eid = eid_factory(type=EntityType.BIO_SEQUENCE)
    file_name = 'bio_sequence'

    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'attributes': {
                'eid': eid,
                'name': file_name,
                'description': '',
                'type': EntityType.BIO_SEQUENCE,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '222',
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = BiologicalSequence.create(
        container=container, name=file_name, content=bio_seq_content, file_extension='gb', force=force
    )

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('entities', container.eid, 'children', f'{file_name}.gb'),
        params={
            'digest': container.digest,
            'force': 'true' if force else 'false',
        },
        headers={
            'Content-Type': 'biosequence/genbank',
        },
        data=bio_seq_content,
    )

    assert isinstance(result, BiologicalSequence)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_get_content(biological_sequence_factory, api_mock, bio_seq_content):
    bio_sequence = biological_sequence_factory()
    file_name = 'bio_sequence.gb'
    content_type = 'biosequence/genbank'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
        'content-length': 1,
    }
    api_mock.call.return_value.content = bio_seq_content

    result = bio_sequence.get_content()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', bio_sequence.eid, 'export'),
        params={
            'format': None,
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content_type == content_type
    assert result.content == bio_seq_content


@pytest.mark.skip('Fix this test after implementing rendering bio sequence in HTML format')
def test_get_html(biological_sequence_factory, snapshot, api_mock, bio_seq_content):
    bio_sequence = biological_sequence_factory(name='name')
    file_name = 'bio_sequence.gb'
    content_type = 'biosequence/genbank'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
        'content-length': 1,
    }
    api_mock.call.return_value.content = bio_seq_content

    bio_seq_html = bio_sequence.get_html()

    snapshot.assert_match(bio_seq_html)
