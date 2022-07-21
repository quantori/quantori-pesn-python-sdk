import pytest

from signals_notebook.attributes import Attribute
from signals_notebook.attributes.attribute import Action
from signals_notebook.common_types import AttrID, ObjectType


@pytest.fixture()
def attribute_response():
    def wrapper(_id: AttrID):
        return {
            'links': {'self': f'https://example.com/api/rest/v1.0/attributes/{_id}'},
            'data': {
                'type': 'attribute',
                'id': _id,
                'links': {'self': f'https://example.com/api/rest/v1.0/attributes/{_id}'},
                'attributes': {
                    'id': _id,
                    'name': 'GHS Signal Words',
                    'type': 'choice',
                    'options': ['WARNING', 'DANGER'],
                    'counts': {'total': 2, 'templates': {'total': 0, 'system': 0}},
                },
            },
        }

    return wrapper


@pytest.fixture()
def attributes_response():
    return {
        'data': [
            {
                'type': 'entity',
                'id': 'attribute:18',
                'links': {'self': 'https://example.com/api/rest/v1.0/entities/attribute:18'},
                'attributes': {
                    'id': 'attribute:18',
                    'eid': 'attribute:18',
                    'name': 'Inventory Security',
                    'type': 'attribute',
                    'digest': '0',
                    'fields': {},
                    'flags': {'canEdit': True},
                },
            },
            {
                'type': 'entity',
                'id': 'attribute:4',
                'links': {'self': 'https://example.com/api/rest/v1.0/entities/attribute:4'},
                'attributes': {
                    'id': 'attribute:4',
                    'eid': 'attribute:4',
                    'name': 'Material Library Type',
                    'type': 'attribute',
                    'digest': '0',
                    'fields': {},
                },
            },
            {
                'type': 'entity',
                'id': 'attribute:26',
                'links': {'self': 'https://example.com/api/rest/v1.0/entities/attribute:26'},
                'attributes': {
                    'id': 'attribute:26',
                    'eid': 'attribute:26',
                    'name': 'newAttribute',
                    'description': 'Test',
                    'type': 'attribute',
                    'digest': '0',
                    'fields': {},
                    'flags': {'canEdit': True},
                },
            },
        ]
    }


@pytest.fixture()
def options_response():
    return {
        'links': {
            'self': 'https://example.com/api/rest/v1.0/attributes/attribute:18/options?page[offset]=0&page[limit]=20',
            'first': 'https://example.com/api/rest/v1.0/attributes/attribute:18/options?page[offset]=0&page[limit]=20',
        },
        'data': [
            {'type': 'option', 'id': 'ladflklsjdf', 'attributes': {'key': 'ladflklsjdf', 'value': 'ladflklsjdf'}},
            {'type': 'option', 'id': 'option2', 'attributes': {'key': 'option2', 'value': 'option2'}},
            {'type': 'option', 'id': 'option3', 'attributes': {'key': 'option3', 'value': 'option3'}},
        ],
    }


@pytest.fixture()
def options_response_for_update():
    def wrapper(value: str):
        return {
            'links': {
                'self': 'https://ex.com/api/rest/v1.0/attributes/attribute:18/options?page[offset]=0&page[limit]=20',
                'first': 'https://ex.com/api/rest/v1.0/attributes/attribute:18/options?page[offset]=0&page[limit]=20',
            },
            'data': [
                {'type': 'option', 'id': 'ladflklsjdf', 'attributes': {'key': 'ladflklsjdf', 'value': 'ladflklsjdf'}},
                {'type': 'option', 'id': 'option2', 'attributes': {'key': 'option2', 'value': value}},
                {'type': 'option', 'id': 'option3', 'attributes': {'key': 'option3', 'value': 'option3'}},
            ],
        }

    return wrapper


@pytest.fixture()
def options_response_for_delete():
    return {
        'links': {
            'self': 'https://example.com/api/rest/v1.0/attributes/attribute:18/options?page[offset]=0&page[limit]=20',
            'first': 'https://example.com/api/rest/v1.0/attributes/attribute:18/options?page[offset]=0&page[limit]=20',
        },
        'data': [
            {'type': 'option', 'id': 'ladflklsjdf', 'attributes': {'key': 'ladflklsjdf', 'value': 'ladflklsjdf'}},
            {'type': 'option', 'id': 'option3', 'attributes': {'key': 'option3', 'value': 'option3'}},
        ],
    }


@pytest.fixture()
def options_response_for_create():
    def wrapper(value: str):
        return {
            'links': {
                'self': 'https://ex.com/api/rest/v1.0/attributes/attribute:18/options?page[offset]=0&page[limit]=20',
                'first': 'https://ex.com/api/rest/v1.0/attributes/attribute:18/options?page[offset]=0&page[limit]=20',
            },
            'data': [
                {'type': 'option', 'id': 'ladflklsjdf', 'attributes': {'key': 'ladflklsjdf', 'value': 'ladflklsjdf'}},
                {'type': 'option', 'id': 'option2', 'attributes': {'key': 'option2', 'value': 'option2'}},
                {'type': 'option', 'id': 'option3', 'attributes': {'key': 'option3', 'value': 'option3'}},
                {'type': 'option', 'id': value, 'attributes': {'key': value, 'value': value}},
            ],
        }

    return wrapper


def test_get(attr_id_factory, api_mock, attribute_response):
    _id = attr_id_factory()

    response = attribute_response(_id)

    api_mock.call.return_value.json.return_value = response

    result = Attribute.get(_id)

    api_mock.call.assert_called_once_with(method='GET', path=('attributes', _id))

    assert isinstance(result, Attribute)
    assert result.type == 'choice'
    assert result.name == response['data']['attributes']['name']
    assert result.id == _id


def test_get_list(api_mock, attributes_response):
    api_mock.call.return_value.json.return_value = attributes_response

    attributes = Attribute.get_list()

    for item in attributes:
        assert isinstance(item, Attribute)

    api_mock.call.assert_called_once_with(method='GET', path=('attributes',))


def test_create(api_mock, attr_id_factory, attribute_response):
    _id = attr_id_factory()
    option_id = 'HEY'
    response = attribute_response(_id)
    api_mock.call.return_value.json.return_value = response

    name = 'test327'
    description = 'descriptions'
    new_attribute = Attribute.create(name=name, type='choice', description=description, options=[option_id])

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('attributes',),
        json={
            'data': {
                'type': ObjectType.ATTRIBUTE,
                'attributes': {
                    'name': name,
                    'type': 'choice',
                    'description': description,
                    'options': [option_id],
                },
            }
        },
    )

    assert isinstance(new_attribute, Attribute)
    assert new_attribute.type == 'choice'
    assert new_attribute.name == response['data']['attributes']['name']
    assert new_attribute.id == _id


def test_add_option(
    api_mock,
    options_response,
    attribute_factory,
    get_response_object,
    options_response_for_create,
    mocker,
):
    attribute = attribute_factory()
    option_value = 'GOGOGOGOGO'

    assert attribute._options == []

    api_mock.call.return_value.json.return_value = options_response
    _ = attribute.options

    assert attribute._options != []

    create_response = options_response_for_create(option_value)
    api_mock.call.side_effect = [get_response_object(create_response), get_response_object(create_response)]
    attribute.add_option(value=option_value)

    api_mock.call.return_value.json.return_value = create_response
    assert len(attribute) == 4

    api_mock.call.assert_has_calls(
        [
            mocker.call(method='GET', path=('attributes', attribute.id, 'options')),
            mocker.call(
                method='PATCH',
                path=('attributes', attribute.id, 'options'),
                json={
                    'data': [
                        {
                            'type': ObjectType.ATTRIBUTE_OPTION,
                            'attributes': {'action': Action.CREATE, 'value': option_value},
                        }
                    ]
                },
            ),
            mocker.call(method='GET', path=('attributes', attribute.id, 'options')),
        ],
        any_order=True,
    )


def test_delete_option(
    api_mock, options_response, attribute_factory, get_response_object, options_response_for_delete, mocker
):
    attribute = attribute_factory()
    option_id = 'option2'

    assert attribute._options == []

    api_mock.call.return_value.json.return_value = options_response
    _ = attribute.options

    assert attribute._options != []

    delete_response = options_response_for_delete
    api_mock.call.side_effect = [get_response_object(delete_response), get_response_object(delete_response)]
    attribute.delete_option(id=option_id)

    assert len(attribute) == 2
    api_mock.call.assert_has_calls(
        [
            mocker.call(method='GET', path=('attributes', attribute.id, 'options')),
            mocker.call(
                method='PATCH',
                path=('attributes', attribute.id, 'options'),
                json={
                    'data': [
                        {
                            'id': option_id,
                            'type': ObjectType.ATTRIBUTE_OPTION,
                            'attributes': {'action': Action.DELETE},
                        }
                    ]
                },
            ),
            mocker.call(method='GET', path=('attributes', attribute.id, 'options')),
        ],
        any_order=True,
    )


def test_update_option(
    api_mock, options_response, attribute_factory, get_response_object, options_response_for_update, mocker
):
    attribute = attribute_factory()
    old_option = 'option2'
    new_option = 'GOGOGOGOGO'

    assert attribute._options == []

    api_mock.call.return_value.json.return_value = options_response
    _ = attribute.options

    assert len(attribute) == 3
    assert attribute._options != []

    update_response = options_response_for_update(old_option)
    api_mock.call.side_effect = [get_response_object(update_response), get_response_object(update_response)]
    attribute.update_option(old_option=old_option, new_option=new_option)

    assert len(attribute) == 3
    api_mock.call.assert_has_calls(
        [
            mocker.call(method='GET', path=('attributes', attribute.id, 'options')),
            mocker.call(
                method='PATCH',
                path=('attributes', attribute.id, 'options'),
                json={
                    'data': [
                        {
                            'id': old_option,
                            'type': ObjectType.ATTRIBUTE_OPTION,
                            'attributes': {'action': Action.UPDATE, 'value': new_option},
                        }
                    ]
                },
            ),
            mocker.call(method='GET', path=('attributes', attribute.id, 'options')),
        ],
        any_order=True,
    )


def test_delete(api_mock, attr_id_factory, attribute_factory):
    _id = attr_id_factory()
    attribute = attribute_factory(id=_id)

    api_mock.call.return_value.json.return_value = ''

    attribute.delete()

    api_mock.call.assert_called_once_with(method='DELETE', path=('attributes', _id))


def test_reload_options(api_mock, options_response, attribute_factory):
    attribute = attribute_factory()

    assert attribute._options == []

    api_mock.call.return_value.json.return_value = options_response
    options = attribute.options

    assert attribute._options != []

    for item in options:
        assert isinstance(item, str)


def test_iter(api_mock, options_response, attribute_factory):
    attribute = attribute_factory()

    assert attribute._options == []

    api_mock.call.return_value.json.return_value = options_response

    for item in attribute:
        assert isinstance(item, str)

    assert attribute._options != []


def test_len(api_mock, options_response, attribute_factory):
    attribute = attribute_factory()

    assert attribute._options == []

    api_mock.call.return_value.json.return_value = options_response

    assert len(attribute) == 3

    for item in attribute:
        assert isinstance(item, str)

    assert attribute._options != []
