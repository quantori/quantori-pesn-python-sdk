import arrow
import pytest

from signals_notebook.common_types import EntityType, File, ObjectType
from signals_notebook.entities import UploadedResource


@pytest.mark.parametrize('digest, force', [('111', False), (None, True)])
def test_create(api_mock, experiment_factory, eid_factory, digest, force):
    container = experiment_factory(digest=digest)
    eid = eid_factory(type=EntityType.UPLOADED_RESOURCE)
    file_name = 'Test.zip'
    content = 'Some text'
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'attributes': {
                'eid': eid,
                'name': file_name,
                'description': '',
                'type': EntityType.UPLOADED_RESOURCE,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '222',
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = UploadedResource.create(container=container, name=file_name, content=content, force=force)

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('entities', container.eid, 'children', file_name),
        params={
            'digest': container.digest,
            'force': 'true' if force else 'false',
        },
        headers={
            'Content-Type': 'application/x-zip-compressed',
        },
        data=content.encode('utf-8'),
    )

    assert isinstance(result, UploadedResource)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_get_content(uploaded_resource_factory, api_mock):
    uploaded_resource = uploaded_resource_factory()
    file_name = 'Test.zip'
    content = b'Some text'
    content_type = 'application/x-zip-compressed'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    result = uploaded_resource.get_content()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', uploaded_resource.eid, 'export'),
        params={
            'format': None,
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type


def test_get_html(uploaded_resource_factory, snapshot, api_mock):
    uploaded_resource = uploaded_resource_factory(name='name')
    file_name = 'Test.zip'
    content = b'Some text'
    content_type = 'application/x-zip-compressed'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    uploaded_resource_html = uploaded_resource.get_html()

    snapshot.assert_match(uploaded_resource_html)
