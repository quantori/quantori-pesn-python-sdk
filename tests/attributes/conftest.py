import pytest
from pytest_factoryboy import register

from tests.attributes.factories import AttributeFactory, AttributeOptionFactory, AttrIDFactory

register(AttrIDFactory)
register(AttributeFactory)
register(AttributeOptionFactory)


@pytest.fixture()
def get_response_object(mocker):
    def _f(response):
        mock = mocker.Mock()
        mock.json.return_value = response
        return mock

    return _f
