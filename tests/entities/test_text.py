import arrow
import pytest

from signals_notebook.entities import Text
from signals_notebook.types import EntityType, EID, ObjectType, File


def test_get_list(api_mock):
    eid1 = EID('text:79b12479-2b5d-490f-be52-d60c53f16719')
    eid2 = EID('text:079b6475-6d41-4256-b61b-46e097bbcbfa')
    response = {
        'links': {'self': f'https://example.com/{eid1}'},
        'data': [
            {
                'type': ObjectType.ENTITY,
                'id': eid1,
                'links': {'self': f'https://example.com/{eid1}'},
                'attributes': {
                    'eid': eid1,
                    'name': 'Text 1',
                    'description': 'test description 1',
                    'type': EntityType.TEXT,
                    'createdAt': '2020-09-06T03:12:35.129Z',
                    'editedAt': '2020-09-06T15:22:47.309Z',
                    'digest': '111',
                },
            },
            {
                'type': ObjectType.ENTITY,
                'id': eid2,
                'links': {'self': f'https://example.com/{eid2}'},
                'attributes': {
                    'eid': eid2,
                    'name': 'Text 2',
                    'description': 'test description 2',
                    'type': EntityType.TEXT,
                    'createdAt': '2021-09-06T03:12:35.129Z',
                    'editedAt': '2021-09-06T15:22:47.309Z',
                    'digest': '222',
                },
            },
        ],
    }
    api_mock.call.return_value.json.return_value = response

    result_generator = Text.get_list()

    api_mock.call.assert_not_called()

    result = list(result_generator)

    api_mock.call.assert_called_once_with(
        method='GET', path=('entities',), params={'includeTypes': EntityType.TEXT}
    )

    for item, raw_item in zip(result, response['data']):
        assert isinstance(item, Text)
        assert item.eid == raw_item['id']
        assert item.digest == raw_item['attributes']['digest']
        assert item.name == raw_item['attributes']['name']
        assert item.description == raw_item['attributes']['description']
        assert item.created_at == arrow.get(raw_item['attributes']['createdAt'])
        assert item.edited_at == arrow.get(raw_item['attributes']['editedAt'])


@pytest.mark.parametrize('digest, force', [('111', False), (None, True)])
def test_create(api_mock, experiment_factory, digest, force):
    container = experiment_factory(digest=digest)
    eid = EID('text:79b12479-2b5d-490f-be52-d60c53f16719')
    file_name = 'Text'
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
                'type': EntityType.TEXT,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '222',
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = Text.create(container=container, name=file_name, content=content, force=force)

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('entities', container.eid, 'children', f'{file_name}.txt'),
        params={
            'digest': container.digest,
            'force': 'true' if force else 'false',
        },
        headers={
            'Content-Type': 'text/plain',
        },
        data=content.encode('utf-8'),
    )

    assert isinstance(result, Text)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


def test_delete(text_factory, api_mock):
    text = text_factory()

    text.delete()

    api_mock.call.assert_called_once_with(
        method='DELETE',
        path=('entities', text.eid),
        params={
            'digest': None,
            'force': 'true',
        },
    )


def test_get_content(text_factory, api_mock):
    text = text_factory()
    file_name = 'Text.txt'
    content = b'Some text'
    content_type = 'text/plain'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}'
    }
    api_mock.call.return_value.content = content

    result = text.get_content()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', text.eid, 'export'),
        params={
            'format': None,
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type


@pytest.mark.parametrize('force', [True, False])
def test_update(api_mock, text_factory, force):
    text = text_factory()

    text.name = 'New name'
    text.description = 'New description'
    text.save(force=force)

    api_mock.call.assert_called_once_with(
        method='PATCH',
        path=('entities', text.eid, 'properties'),
        params={
            'digest': None if force else text.digest,
            'force': 'true' if force else 'false',
        },
        json={
            'data': [
                {'attributes': {'name': 'Name', 'value': 'New name'}},
                {'attributes': {'name': 'Description', 'value': 'New description'}},
            ]
        },
    )
