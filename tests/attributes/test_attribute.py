import pytest

from signals_notebook.attributes import Attribute, AttributeOption
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
        "data": [
            {
                "type": "entity",
                "id": "attribute:18",
                "links": {"self": "https://example.com/api/rest/v1.0/entities/attribute:18"},
                "attributes": {
                    "id": "attribute:18",
                    "eid": "attribute:18",
                    "name": "Inventory Security",
                    "type": "attribute",
                    "digest": "0",
                    "fields": {},
                    "flags": {"canEdit": True},
                },
            },
            {
                "type": "entity",
                "id": "attribute:4",
                "links": {"self": "https://example.com/api/rest/v1.0/entities/attribute:4"},
                "attributes": {
                    "id": "attribute:4",
                    "eid": "attribute:4",
                    "name": "Material Library Type",
                    "type": "attribute",
                    "digest": "0",
                    "fields": {},
                },
            },
            {
                "type": "entity",
                "id": "attribute:26",
                "links": {"self": "https://example.com/api/rest/v1.0/entities/attribute:26"},
                "attributes": {
                    "id": "attribute:26",
                    "eid": "attribute:26",
                    "name": "newAttribute",
                    "description": "Test",
                    "type": "attribute",
                    "digest": "0",
                    "fields": {},
                    "flags": {"canEdit": True},
                },
            },
        ]
    }


@pytest.fixture()
def options_response():
    return {
        "links": {
            "self": "https://example.com/api/rest/v1.0/attributes/attribute:18/options?page[offset]=0&page[limit]=20",
            "first": "https://example.com/api/rest/v1.0/attributes/attribute:18/options?page[offset]=0&page[limit]=20",
        },
        "data": [
            {"type": "option", "id": "ladflklsjdf", "attributes": {"key": "ladflklsjdf", "value": "ladflklsjdf"}},
            {"type": "option", "id": "option2", "attributes": {"key": "option2", "value": "option2"}},
            {"type": "option", "id": "option3", "attributes": {"key": "option3", "value": "option3"}},
        ],
    }


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


def test_create(api_mock, attr_id_factory, attribute_option_factory, attribute_response):
    _id = attr_id_factory()
    option = attribute_option_factory()
    response = attribute_response(_id)
    api_mock.call.return_value.json.return_value = response

    name = 'test327'
    description = 'descriptions'
    new_attribute = Attribute.create(name=name, type='choice', description=description, options=[option])

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
                    'options': [option.id],
                },
            }
        },
    )

    assert isinstance(new_attribute, Attribute)
    assert new_attribute.type == 'choice'
    assert new_attribute.name == response['data']['attributes']['name']
    assert new_attribute.id == _id


def test_append(api_mock):
    pass


def test_save(api_mock):
    pass


def test_delete(api_mock, attr_id_factory, attribute_factory):
    _id = attr_id_factory()
    attribute = attribute_factory(id=_id)

    api_mock.call.return_value.json.return_value = ''

    attribute.delete()

    api_mock.call.assert_called_once_with(method='DELETE', path=('attributes', _id))


def test_reload_options(api_mock, options_response, attribute_factory):
    attribute = attribute_factory()

    assert attribute._options == []
    assert attribute._options_by_id == {}

    api_mock.call.return_value.json.return_value = options_response
    options = attribute.options

    assert attribute._options != []
    assert attribute._options_by_id != {}

    for item in options:
        assert isinstance(item, AttributeOption)


@pytest.mark.parametrize('index', [1, 0, 2, 'ladflklsjdf', 'option2', 'option3'])
def test_getitem(api_mock, options_response, attribute_factory, index):
    attribute = attribute_factory()

    assert attribute._options == []
    assert attribute._options_by_id == {}

    api_mock.call.return_value.json.return_value = options_response

    assert isinstance(attribute[index], AttributeOption)

    assert attribute._options != []
    assert attribute._options_by_id != {}


def test_iter(api_mock, options_response, attribute_factory):
    attribute = attribute_factory()

    assert attribute._options == []
    assert attribute._options_by_id == {}

    api_mock.call.return_value.json.return_value = options_response

    for item in attribute:
        assert isinstance(item, AttributeOption)

    assert attribute._options != []
    assert attribute._options_by_id != {}


def test_len(api_mock, options_response, attribute_factory):
    attribute = attribute_factory()

    assert attribute._options == []
    assert attribute._options_by_id == {}

    api_mock.call.return_value.json.return_value = options_response

    assert len(attribute) == 3

    for item in attribute:
        assert isinstance(item, AttributeOption)

    assert attribute._options != []
    assert attribute._options_by_id != {}
