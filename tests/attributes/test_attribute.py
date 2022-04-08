import pytest

from signals_notebook.attributes import Attribute


def test_get(attr_id_factory, api_mock):
    id = attr_id_factory()

    response = {
        'links': {'self': f'https://quantori.signalsnotebook.perkinelmer.cloud/api/rest/v1.0/attributes/{id}'},
        'data': {
            'type': 'attribute',
            'id': id,
            'links': {
                'self': f'https://quantori.signalsnotebook.perkinelmer.cloud/api/rest/v1.0/attributes/{id}'
            },
            'attributes': {
                'id': id,
                'name': 'GHS Signal Words',
                'type': 'choice',
                'options': ['WARNING', 'DANGER'],
                'counts': {'total': 2, 'templates': {'total': 0, 'system': 0}},
            },
        },
    }

    api_mock.call.return_value.json.return_value = response

    result = Attribute.get(id)

    api_mock.call.assert_called_once_with(method='GET', path=('attributes', id))

    assert isinstance(result, Attribute)
    assert result.type == 'choice'
    assert result.name == response['data']['attributes']['name']
    assert result.id == id
    assert result.options == response['data']['attributes']['options']


def test_check_correct_value(attribute_factory):
    attribute = attribute_factory(name='test')

    assert attribute('test 1') == 'test 1'


def test_check_incorrect_value(attribute_factory):
    attribute = attribute_factory(name='test')

    with pytest.raises(ValueError) as e:
        attribute('test 10')

    assert str(e.value) == 'Incorrect attribute value'
