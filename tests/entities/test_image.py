import base64 as b64

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
