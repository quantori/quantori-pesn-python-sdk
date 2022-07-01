import pytest

from signals_notebook.entities import TaskCell


def test_reload_properties(api_mock, task_factory, task_properties):
    task = task_factory()

    assert task._cells == []

    api_mock.call.return_value.json.return_value = task_properties
    for item in task:
        assert isinstance(item, TaskCell)

    assert task._cells != []

    api_mock.call.assert_called_once_with(
        method='GET',
        path=(task._get_tasks_endpoint(), task.eid, 'properties'),
        params={
            'value': 'normalized',
        },
    )


def test_save(api_mock, task_factory, task_properties, mocker):
    task = task_factory()

    assert task._cells == []

    api_mock.call.return_value.json.return_value = task_properties
    for item in task:
        if item.id == '4':
            item.content.set_value('5545')
    api_mock.call.return_value.json.return_value = {}
    api_mock.call.return_value.json.return_value = task_properties

    assert task._cells != []

    request_body = []
    for item in task:
        if item.is_changed:
            request_body.append(item.representation_for_update.dict(exclude_none=True))

    task.save()

    api_mock.call.assert_has_calls(
        [
            mocker.call(
                method='GET',
                path=(task._get_tasks_endpoint(), task.eid, 'properties'),
                params={
                    'value': 'normalized',
                },
            ),
            mocker.call(
                method='PATCH',
                path=(task._get_tasks_endpoint(), task.eid, 'properties'),
                params={
                    'force': 'true',
                    'value': 'normalized',
                },
                json={
                    'data': {'attributes': {'data': request_body}},
                },
            ),
        ],
        any_order=True,
    )


@pytest.mark.parametrize(
    'index', [1, '3']
)
def test_getitem(api_mock, task_factory, task_properties, index):
    task = task_factory()

    assert task._cells == []

    api_mock.call.return_value.json.return_value = task_properties

    for item in task:
        assert isinstance(item, TaskCell)

    assert isinstance(task[index], TaskCell)
    assert task._cells != []


def test_iter(api_mock, task_factory, task_properties):
    task = task_factory()

    assert task._cells == []

    api_mock.call.return_value.json.return_value = task_properties

    for item in task:
        assert isinstance(item, TaskCell)

    assert task._cells != []
