import json

import arrow
import pytest

from signals_notebook.common_types import EntityType, File, ObjectType
from signals_notebook.entities import Excel


@pytest.mark.parametrize('digest, force', [('111', False), (None, True)])
def test_create(api_mock, experiment_factory, eid_factory, digest, force):
    container = experiment_factory(digest=digest)
    eid = eid_factory(type=EntityType.EXCEL)
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
                'type': EntityType.EXCEL,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '222',
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = Excel.create(container=container, name=file_name, content=content, force=force)

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('entities', container.eid, 'children', f'{file_name}.xlsx'),
        params={
            'digest': container.digest,
            'force': 'true' if force else 'false',
        },
        headers={
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        },
        data=content,
    )

    assert isinstance(result, Excel)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_get_content(excel_factory, api_mock):
    excel = excel_factory()
    file_name = 'Test.xlsx'
    content = b'Some text'
    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    result = excel.get_content()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', excel.eid, 'export'),
        params={
            'format': None,
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type


def test_get_html(excel_factory, snapshot, api_mock):
    excel = excel_factory(name='name')
    file_name = 'Test.xlsx'
    content = b'Some text'
    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    excel_html = excel.get_html()

    snapshot.assert_match(excel_html)


def test_dump(excel_factory, mocker, api_mock):
    excel = excel_factory(name='name')
    file_name = 'Test.xlsx'
    content = b'Some text'
    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

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
        **{k: v for k, v in excel.dict().items() if k in ('name', 'description', 'eid')},
    }
    excel.dump(base_path=base_path, fs_handler=fs_handler_mock)

    join_path_call_1 = mocker.call(base_path, excel.eid, 'metadata.json')
    join_path_call_2 = mocker.call(base_path, excel.eid, file_name)

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
    eid = eid_factory(type=EntityType.EXCEL)
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
                'type': EntityType.EXCEL,
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

    Excel.load(path=base_path, fs_handler=fs_handler_mock, parent=container)

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
        path=('entities', container.eid, 'children', f'{file_name}.xlsx'),
        params={
            'digest': None,
            'force': 'true',
        },
        headers={
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        },
        data=content,
    )
