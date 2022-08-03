import json
from uuid import UUID
import os
import pytest

from signals_notebook.common_types import EntityType
from signals_notebook.entities.parallel_experiment.row import Row


@pytest.fixture()
def get_response(mocker):
    def _f(response):
        mock = mocker.Mock()
        mock.status_code = 200
        mock.json.return_value = response
        return mock

    return _f


@pytest.fixture()
def reload_data_response():
    path = os.path.join(os.path.dirname(__file__), 'reload_data_response.json')
    with open(path, 'r') as f:
        response = json.load(f)

    return response


@pytest.fixture()
def updated_reload_data_response():
    path = os.path.join(os.path.dirname(__file__), 'updated_reload_data_response.json')
    with open(path, 'r') as f:
        response = json.load(f)

    return response


def test_reload_properties(api_mock, reload_data_response, sub_experiment_summary_factory):
    sub_experiment_summary = sub_experiment_summary_factory()

    assert sub_experiment_summary._rows == []

    api_mock.call.return_value.json.return_value = reload_data_response

    for item in sub_experiment_summary:
        assert isinstance(item, Row)

    assert sub_experiment_summary._rows != []

    api_mock.call.assert_called_once_with(
        method='GET',
        path=(sub_experiment_summary._get_endpoint(), sub_experiment_summary.eid, 'rows'),
    )


def test_save(
    api_mock,
    reload_data_response,
    updated_reload_data_response,
    sub_experiment_summary_factory,
    mocker,
    eid_factory,
    get_response,
):
    subexp_sum_eid = eid_factory(type=EntityType.SUB_EXPERIMENT_SUMMARY)

    update_response = {
        "links": {"self": "https://example.com/subexpSummary/paragrid:3f46e915-cf66-4957-abb0-1566861c7760/bulkUpdate"},
        "data": {
            "type": "bulkUpdateParagrid",
            "id": subexp_sum_eid,
            "attributes": {
                "subexpSummaryId": subexp_sum_eid,
                "bulkUpdateId": 20,
                "description": "We have created a job to execute it. Follow the status link to check the status.",
            },
            "relationships": {
                "status": {
                    "links": {"self": f"https://example.com/subexpSummary/{subexp_sum_eid}/bulkUpdate/20"},
                    "data": {"type": "subexpSummaryBulkUpdateReport", "id": "20"},
                }
            },
        },
    }
    update_status_response = {
        "links": {"self": f"https://example.com/subexpSummary/{subexp_sum_eid}/20"},
        "data": {
            "type": "subexpSummaryBulkUpdateReport",
            "id": "20",
            "links": {"self": f"https://example.com/subexpSummary/{subexp_sum_eid}/bulkUpdate/20"},
            "attributes": {
                "bulkUpdateId": 20,
                "subexpSummaryId": subexp_sum_eid,
                "jobType": "ASYNC_TASK",
                "state": "SCHEDULED",
                "jobStatus": "SUCCESS",
                "digest": "B7wcvn7GJZFeXh9APOvdhnutfnP9fWufdIlyhDX/GmWBC/dztZMTsXXLthSF2sB8BNQ80q63Tgj0s6HeOBSX1A==",
            },
        },
    }
    sub_experiment_summary = sub_experiment_summary_factory()

    assert sub_experiment_summary._rows == []

    api_mock.call.return_value.json.return_value = reload_data_response

    sub_experiment_summary[0]["p1:name"].set_value('Updated Text 1')

    api_mock.call.side_effect = [
        get_response(update_response),
        get_response(update_status_response),
        get_response(updated_reload_data_response),
    ]

    request_body = []
    for item in sub_experiment_summary._rows:
        if item.is_changed:
            request_body.extend(item.representation_for_update)

    sub_experiment_summary.save()

    update_id = update_response['data']['attributes']['bulkUpdateId']
    api_mock.call.assert_has_calls(
        [
            mocker.call(
                method='GET',
                path=(sub_experiment_summary._get_endpoint(), sub_experiment_summary.eid, 'rows'),
            ),
            mocker.call(
                method='PATCH',
                path=(sub_experiment_summary._get_endpoint(), sub_experiment_summary.eid, 'bulkUpdate'),
                params={
                    'force': 'true',
                },
                json={
                    'data': request_body,
                },
            ),
            mocker.call(
                method='GET',
                path=(sub_experiment_summary._get_endpoint(), sub_experiment_summary.eid, 'bulkUpdate', str(update_id)),
            ),
            mocker.call(
                method='GET',
                path=(sub_experiment_summary._get_endpoint(), sub_experiment_summary.eid, 'rows'),
            ),
        ],
        any_order=True,
    )


@pytest.mark.parametrize(
    'index', [0, 'ee8f5e33-aaea-44f0-b429-aef793807585', UUID('ee8f5e33-aaea-44f0-b429-aef793807585')]
)
def test_getitem(api_mock, reload_data_response, sub_experiment_summary_factory, index):
    api_mock.call.return_value.json.return_value = reload_data_response
    sub_experiment_summary = sub_experiment_summary_factory()
    assert isinstance(sub_experiment_summary[index], Row)


def test_getitem_with_invalid_index(api_mock, reload_data_response, sub_experiment_summary_factory):
    api_mock.call.return_value.json.return_value = reload_data_response

    sub_experiment_summary = sub_experiment_summary_factory()

    with pytest.raises(IndexError) as e:
        sub_experiment_summary[1.5]

    assert str(e.value) == 'Invalid index'


def test_iter(api_mock, reload_data_response, sub_experiment_summary_factory):
    sub_experiment_summary = sub_experiment_summary_factory()

    api_mock.call.return_value.json.return_value = reload_data_response

    for row in sub_experiment_summary:
        assert isinstance(row, Row)
