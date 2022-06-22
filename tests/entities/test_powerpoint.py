import arrow
import pytest

from signals_notebook.common_types import EntityType, File, ObjectType
from signals_notebook.entities import PowerPoint


@pytest.mark.parametrize('digest, force', [('111', False), (None, True)])
def test_create(api_mock, experiment_factory, eid_factory, digest, force):
    container = experiment_factory(digest=digest)
    eid = eid_factory(type=EntityType.POWER_POINT)
    file_name = 'Presentation'
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
                'type': EntityType.POWER_POINT,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '222',
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = PowerPoint.create(container=container, name=file_name, content=content, force=force)

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('entities', container.eid, 'children', f'{file_name}.pptx'),
        params={
            'digest': container.digest,
            'force': 'true' if force else 'false',
        },
        headers={
            'Content-Type': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        },
        data=content.encode('utf-8'),
    )

    assert isinstance(result, PowerPoint)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_get_content(power_point_factory, api_mock):
    power_point = power_point_factory()
    file_name = 'Presentation.pptx'
    content = b'Some text'
    content_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}'
    }
    api_mock.call.return_value.content = content

    result = power_point.get_content()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', power_point.eid, 'export'),
        params={
            'format': None,
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type


def test_get_html(power_point_factory, snapshot, api_mock):
    power_point = power_point_factory(name='name')
    file_name = 'Presentation.pptx'
    content = b'Some text'
    content_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}'
    }
    api_mock.call.return_value.content = content

    power_point_html = power_point.get_html()

    snapshot.assert_match(power_point_html)
