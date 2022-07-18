import json

import arrow
import pytest

from signals_notebook.common_types import EntityType, File, ObjectType
from signals_notebook.entities import PowerPoint


@pytest.mark.parametrize('digest, force', [('111', False), (None, True)])
def test_create(api_mock, experiment_factory, eid_factory, digest, force):
    container = experiment_factory(digest=digest)
    eid = eid_factory(type=EntityType.POWER_POINT)
    file_name = 'Presentation'
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
        data=content,
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
        'content-disposition': f'attachment; filename={file_name}',
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
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    power_point_html = power_point.get_html()

    snapshot.assert_match(power_point_html)


def test_dump(api_mock, power_point_factory, mocker):
    power_point = power_point_factory()
    file_name = 'Presentation.pptx'
    content = b'Some text'
    content_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'

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
        **{k: v for k, v in power_point.dict().items() if k in ('name', 'description', 'eid')},
    }
    power_point.dump(base_path=base_path, fs_handler=fs_handler_mock)

    join_path_call_1 = mocker.call(base_path, power_point.eid, 'metadata.json')
    join_path_call_2 = mocker.call(base_path, power_point.eid, file_name)

    fs_handler_mock.join_path.assert_has_calls(
        [
            join_path_call_1,
            join_path_call_2,
        ],
        any_order=True,
    )
    fs_handler_mock.write.assert_has_calls(
        [
            mocker.call(fs_handler_mock.join_path(), json.dumps(metadata)),
            mocker.call(fs_handler_mock.join_path(), content),
        ],
        any_order=True,
    )


def test_load(api_mock, experiment_factory, eid_factory, mocker):
    container = experiment_factory()
    eid = eid_factory(type=EntityType.POWER_POINT)
    file_name = 'Presentation'
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
                'type': EntityType.POWER_POINT,
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

    PowerPoint.load(path=base_path, fs_handler=fs_handler_mock, parent=container)

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
        path=('entities', container.eid, 'children', f'{file_name}.pptx'),
        params={
            'digest': None,
            'force': 'true',
        },
        headers={
            'Content-Type': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        },
        data=content,
    )

