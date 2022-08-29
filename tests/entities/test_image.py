import base64 as b64
import json

import arrow
import pytest

from signals_notebook.common_types import EntityType, File, ObjectType
from signals_notebook.entities import Image


@pytest.mark.parametrize('digest, force', [('111', False), (None, True)])
def test_create(api_mock, experiment_factory, eid_factory, digest, force):
    container = experiment_factory(digest=digest)
    eid = eid_factory(type=EntityType.IMAGE_RESOURCE)
    file_name = 'image'
    content = b'image content'
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'attributes': {
                'eid': eid,
                'name': file_name,
                'description': '',
                'type': EntityType.IMAGE_RESOURCE,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '222',
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = Image.create(container=container, name=file_name, content=content, content_type='image/png', force=force)

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('entities', container.eid, 'children', f'{file_name}.png'),
        params={
            'digest': container.digest,
            'force': 'true' if force else 'false',
        },
        headers={
            'Content-Type': 'image/png',
        },
        data=content,
    )

    assert isinstance(result, Image)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


@pytest.mark.parametrize('base64', [False, True])
def test_get_content(image_factory, api_mock, base64):
    image = image_factory()
    file_name = 'image.png'
    content = b'image content'
    content_type = 'image/png'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    result = image.get_content(base64=base64)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', image.eid, 'export'),
        params={
            'format': None,
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content_type == content_type
    if base64:
        assert result.content == b64.b64encode(content)
    else:
        assert result.content == content


def test_get_html(image_factory, snapshot, api_mock):
    image = image_factory(name='name')
    file_name = 'image.png'
    content = b'image content'
    content_type = 'image/png'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    image_html = image.get_html()

    snapshot.assert_match(image_html)


def test_dump(image_factory, mocker, api_mock):
    image = image_factory(name='name')
    file_name = 'image.png'
    content = b'image content'
    content_type = 'image/png'

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
        **{k: v for k, v in image.dict().items() if k in ('name', 'description', 'eid')},
    }
    image.dump(base_path=base_path, fs_handler=fs_handler_mock)

    join_path_call_1 = mocker.call(base_path, image.eid, 'metadata.json')
    join_path_call_2 = mocker.call(base_path, image.eid, file_name)

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


@pytest.mark.parametrize(
    'content_type, file_extension',
    [
        ('image/png', 'png'),
        ('image/jpeg', 'jpg'),
        ('image/svg+xml', 'svg'),
    ],
)
def test_load(api_mock, experiment_factory, eid_factory, mocker, content_type, file_extension):
    container = experiment_factory()
    eid = eid_factory(type=EntityType.IMAGE_RESOURCE)
    file_name = 'image'
    content = b'image content'
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'attributes': {
                'eid': eid,
                'name': file_name,
                'description': '',
                'type': EntityType.IMAGE_RESOURCE,
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
        'content_type': content_type
    }
    api_mock.call.return_value.json.return_value = response
    fs_handler_mock.read.side_effect = [json.dumps(metadata), content]
    fs_handler_mock.join_path.side_effect = [base_path + 'metadata.json', base_path + file_name]

    Image.load(path=base_path, fs_handler=fs_handler_mock, parent=container)

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
        path=('entities', container.eid, 'children', f'{file_name}.{file_extension}'),
        params={
            'digest': None,
            'force': 'true',
        },
        headers={
            'Content-Type': content_type,
        },
        data=content,
    )
