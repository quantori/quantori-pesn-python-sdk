import pytest

from signals_notebook.common_types import EID, File
from signals_notebook.entities import Task, TaskCell


@pytest.fixture()
def get_response(mocker):
    def _f(response):
        mock = mocker.Mock()
        mock.status_code = 200
        mock.json.return_value = response
        return mock

    return _f


@pytest.fixture()
def task_container_content():
    return (
        b'{"cols":[{"key":"1","title":"Task ID","type":"link","isEditableInRequest":false,'
        b'"isEditableInExperiment":false,"isTaskIdField":true,"internalSearchQuery":{}}, {"key":"2","title":"Task '
        b'Type","type":"text","isEditableInRequest":false,"isEditableInExperiment":false},{"key":"3",'
        b'"title":"Reference ID","type":"link","isEditableInRequest":true,"isEditableInExperiment":false}],'
        b'"rows":[{"_id":"VALUE","sourceEid":"task:VALUE","eid":"task:58ebedd9-c158-4bf3-b737-b45aea636a61",'
        b'"1":{"auto":"Task-4","value":"task:VALUE","type":"task"},"2":{"auto":"Task","value":"Task"},'
        b'"3":{"user":"Synthesis of SPI", "value":"experiment:VALUE","type":"experiment"}}]} '
    )


@pytest.fixture()
def get_task():
    return {
        'links': {'self': 'https://example.com/api/rest/v1.0/entities/task:58ebedd9-c158-4bf3-b737-b45aea636a61'},
        'data': {
            'type': 'entity',
            'id': 'task:58ebedd9-c158-4bf3-b737-b45aea636a61',
            'links': {'self': 'https://example.com/api/rest/v1.0/entities/task:58ebedd9-c158-4bf3-b737-b45aea636a61'},
            'attributes': {
                'id': 'task:58ebedd9-c158-4bf3-b737-b45aea636a61',
                'eid': 'task:58ebedd9-c158-4bf3-b737-b45aea636a61',
                'name': 'Task-4',
                'description': '',
                'createdAt': '2021-11-11T11:31:32.289Z',
                'editedAt': '2022-06-23T14:45:09.842Z',
                'type': 'task',
                'digest': '55294225',
                'fields': {
                    'Description': {'value': ''},
                    'Name': {'value': 'Task-4'},
                    'Status': {'value': 'In Progress'},
                },
            },
        },
    }


def test_get_content(task_container_factory, api_mock, task_container_content):
    task_container = task_container_factory(name='name')
    file_name = 'Test.txt'
    content = task_container_content
    content_type = 'text/txt'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    result = task_container.get_content()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', task_container.eid, 'export'),
        params={
            'format': None,
        },
    )
    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type


def test_get_html(task_container_factory, snapshot, api_mock, task_container_content):
    task_container = task_container_factory(name='name')
    file_name = 'Test.txt'
    content = task_container_content
    content_type = 'text/txt'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    task_container_html = task_container.get_html()

    snapshot.assert_match(task_container_html)


def test_reload_tasks(api_mock, task_container_factory, task_properties, task_container_content, get_task, mocker):
    task_container = task_container_factory()

    assert task_container._tasks == []
    assert task_container._tasks_by_id == {}

    file_name = 'Test.txt'
    content = task_container_content
    content_type = 'text/txt'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content
    api_mock.call.return_value.json.return_value = get_task

    task_id = get_task['data']['id']

    for task in task_container:
        assert isinstance(task, Task)
        api_mock.call.return_value.json.return_value = task_properties
        task_property = task[0]
        assert isinstance(task_property, TaskCell)

        for item in task:
            assert isinstance(item, TaskCell)

    assert task_container._tasks != []
    assert task_container._tasks_by_id != {}

    api_mock.call.assert_has_calls(
        [
            mocker.call(
                method='GET',
                path=('entities', task_id),
            ),
            mocker.call(
                method='GET',
                path=('entities', task_container.eid, 'export'),
                params={'format': None},
            ),
            mocker.call(
                method='GET',
                path=(
                    'tasks',
                    task_id,
                    'properties',
                ),
                params={
                    'value': 'normalized',
                },
            ),
        ],
        any_order=True,
    )


def test_save(
    api_mock, task_container_factory, task_properties, task_container_content, get_task, get_response, mocker
):
    task_container = task_container_factory()

    assert task_container._tasks == []
    assert task_container._tasks_by_id == {}

    file_name = 'Test.txt'
    content = task_container_content
    content_type = 'text/txt'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content
    api_mock.call.return_value.json.return_value = get_task

    task_id = get_task['data']['id']

    patch_calls = []
    api_calls = []
    for task in task_container:
        request_body = []

        assert isinstance(task, Task)
        api_mock.call.return_value.json.return_value = task_properties

        for item in task:
            if item.id == '4':
                item.content.set_value('5545')

        api_calls.append(get_response({}))
        api_calls.append(get_response(task_properties))

        for item in task:
            if item.is_changed:
                request_body.append(item.representation_for_update.dict(exclude_none=True))

        patch_calls.append(
            mocker.call(
                method='PATCH',
                path=('tasks', task_id, 'properties'),
                params={
                    'force': 'true',
                    'value': 'normalized',
                },
                json={
                    'data': {'attributes': {'data': request_body}},
                },
            )
        )

    assert task_container._tasks != []
    assert task_container._tasks_by_id != {}

    content_response = get_response({})
    content_response.content = content
    content_response.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.side_effect = [*api_calls, content_response, get_response(get_task)]
    task_container.save()

    api_mock.call.assert_has_calls(
        [
            mocker.call(
                method='GET',
                path=('entities', task_id),
            ),
            mocker.call(
                method='GET',
                path=('entities', task_container.eid, 'export'),
                params={'format': None},
            ),
            mocker.call(
                method='GET',
                path=(
                    'tasks',
                    task_id,
                    'properties',
                ),
                params={
                    'value': 'normalized',
                },
            ),
            *patch_calls,
        ],
        any_order=True,
    )


@pytest.mark.parametrize(
    'index', [0, 'task:58ebedd9-c158-4bf3-b737-b45aea636a61', EID('task:58ebedd9-c158-4bf3-b737-b45aea636a61')]
)
def test_getitem(api_mock, task_container_factory, task_container_content, get_task, index):
    task_container = task_container_factory()

    assert task_container._tasks == []
    assert task_container._tasks_by_id == {}

    file_name = 'Test.txt'
    content = task_container_content
    content_type = 'text/txt'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content
    api_mock.call.return_value.json.return_value = get_task

    task = task_container[0]
    assert isinstance(task, Task)

    assert task_container._tasks != []
    assert task_container._tasks_by_id != {}

    assert isinstance(task_container[index], Task)


def test_iter(api_mock, task_container_factory, task_container_content, task_properties, get_task):
    task_container = task_container_factory()

    assert task_container._tasks == []
    assert task_container._tasks_by_id == {}

    file_name = 'Test.txt'
    content = task_container_content
    content_type = 'text/txt'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content
    api_mock.call.return_value.json.return_value = get_task

    for task in task_container:
        assert isinstance(task, Task)

        api_mock.call.return_value.json.return_value = task_properties

        for item in task:
            assert isinstance(item, TaskCell)

    assert task_container._tasks != []
    assert task_container._tasks_by_id != {}
