import json

import arrow
import pytest

from signals_notebook.common_types import EntityType, File, ObjectType
from signals_notebook.entities import Word


@pytest.mark.parametrize('digest, force', [('111', False), (None, True)])
def test_create(api_mock, experiment_factory, eid_factory, digest, force):
    container = experiment_factory(digest=digest)
    eid = eid_factory(type=EntityType.WORD)
    file_name = 'Test'
    content = b'Some text'
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'attributes': {
                'eid': eid,
                'name': file_name,
                'description': '',
                'type': EntityType.WORD,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '222',
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = Word.create(container=container, name=file_name, content=content, force=force)

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('entities', container.eid, 'children', f'{file_name}.docx'),
        params={
            'digest': container.digest,
            'force': 'true' if force else 'false',
        },
        headers={
            'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        },
        data=content,
    )

    assert isinstance(result, Word)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_get_content(word_factory, api_mock):
    word = word_factory()
    file_name = 'Test.docx'
    content = b'Some text'
    content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    result = word.get_content()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', word.eid, 'export'),
        params={
            'format': None,
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type


def test_get_html(word_factory, snapshot, api_mock):
    word = word_factory(name='name')
    file_name = 'Test.docx'
    content = b'Some text'
    content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    word_html = word.get_html()

    snapshot.assert_match(word_html)


def test_dump(word_factory, api_mock, mocker):
    word = word_factory(name='name')
    file_name = 'Test.docx'
    content = b'Some text'
    content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content
    fs_handler_mock = mocker.MagicMock()
    base_path = './'
    metadata = {
        'file_name': file_name,
        'content_type': content_type,
        **{k: v for k, v in word.dict().items() if k in ('name', 'description', 'eid')},
    }
    word.dump(base_path=base_path, fs_handler=fs_handler_mock)

    join_path_call_1 = mocker.call(base_path, word.eid, 'metadata.json')
    join_path_call_2 = mocker.call(base_path, word.eid, file_name)

    fs_handler_mock.join_path.assert_has_calls(
        [
            join_path_call_1,
            join_path_call_2,
        ],
        any_order=True,
    )
    fs_handler_mock.write.assert_has_calls(
        [
            mocker.call(fs_handler_mock.join_path(), json.dumps(metadata), None),
            mocker.call(fs_handler_mock.join_path(), content, None),
        ],
        any_order=True,
    )


def test_load(api_mock, experiment_factory, eid_factory, mocker):
    container = experiment_factory()
    eid = eid_factory(type=EntityType.WORD)
    file_name = 'Test'
    content = b'Some text'
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'attributes': {
                'eid': eid,
                'name': file_name,
                'description': '',
                'type': EntityType.WORD,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '222',
            },
        },
    }

    fs_handler_mock = mocker.MagicMock()
    base_path = './'
    metadata = {
        'file_name': file_name,
        'name': file_name,
    }
    api_mock.call.return_value.json.return_value = response
    fs_handler_mock.read.side_effect = [json.dumps(metadata), content]
    fs_handler_mock.join_path.side_effect = [base_path + 'metadata.json', base_path + file_name]

    Word.load(path=base_path, fs_handler=fs_handler_mock, parent=container)

    fs_handler_mock.join_path.assert_has_calls(
        [
            mocker.call(base_path, 'metadata.json'),
            mocker.call(base_path, file_name),
        ],
        any_order=True,
    )

    fs_handler_mock.read.assert_has_calls(
        [
            mocker.call(base_path + 'metadata.json'),
            mocker.call(base_path + file_name),
        ],
        any_order=True,
    )

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('entities', container.eid, 'children', f'{file_name}.docx'),
        params={
            'digest': None,
            'force': 'true',
        },
        headers={
            'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        },
        data=content,
    )
