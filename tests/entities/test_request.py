import datetime
import json

import pytest


@pytest.fixture()
def templates():
    return {
        "links": {
            "self": "https://ex.com/api/rest/v1.0/entities?"
                    "includeTypes=request&includeOptions=template&page[offset]=0&page[limit]=20",
            "first": "https://ex.com/api/rest/v1.0/entities?"
                     "includeTypes=request&includeOptions=template&page[offset]=0&page[limit]=20",
        },
        "data": [
            {
                "type": "entity",
                "id": "request:3ef030aa-23c3-4d2f-8ff7-5de6c2870250",
                "links": {
                    "self": "https://ex.com/api/rest/v1.0/entities/request:3ef030aa-23c3-4d2f-8ff7-5de6c2870250"
                },
                "attributes": {
                    "id": "request:3ef030aa-23c3-4d2f-8ff7-5de6c2870250",
                    "eid": "request:3ef030aa-23c3-4d2f-8ff7-5de6c2870250",
                    "name": "DEFAULT_REQUEST",
                    "description": "",
                    "createdAt": "2021-10-22T13:36:06.333Z",
                    "editedAt": "2021-10-22T13:36:06.333Z",
                    "type": "request",
                    "digest": "10841722",
                    "fields": {"Description": {"value": ""}, "Name": {"value": "DEFAULT_REQUEST"}},
                    "flags": {"canEdit": True},
                },
            },
        ],
    }


def test_create():
    pass


def test_create_with_ancestors():
    pass


def test_create_with_template():
    pass


def test_add_children():
    pass


def test_get_children__one_page():
    pass


def test_get_children__several_pages():
    pass


def test_get_html(api_mock, request_container_factory, snapshot):
    request = request_container_factory(
        name='name',
        description='text',
        edited_at=datetime.datetime(2018, 6, 1, 1, 1, 1),
        children=[],
    )
    response = {
        'links': {'self': f'https://example.com/{request.eid}/children'},
        'data': [],
    }
    api_mock.call.return_value.json.return_value = response

    request_html = request.get_html()
    snapshot.assert_match(request_html)


def test_dump_templates(api_mock, mocker, request_container_factory, templates, get_response_object):
    request = request_container_factory(name='name')
    template_eid = templates['data'][0]['id']
    template_name = templates['data'][0]['attributes']['name']
    template_description = templates['data'][0]['attributes']['description']

    fs_handler_mock = mocker.MagicMock()
    base_path = './'
    metadata = {
        'eid': template_eid,
        'name': template_name,
        'description': template_description,
    }

    api_mock.call.side_effect = [get_response_object(templates), get_response_object('')]
    request.dump_templates(base_path=base_path, fs_handler=fs_handler_mock)

    join_path_call_1 = mocker.call(base_path, 'templates', request.type)
    join_path_call_2 = mocker.call(fs_handler_mock.join_path(), template_eid, 'metadata.json')

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
        ],
        any_order=True,
    )


def test_dump():
    pass
