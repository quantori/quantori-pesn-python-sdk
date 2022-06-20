from pytest_factoryboy import register

from tests.attributes.factories import AttributeFactory, AttrIDFactory

register(AttrIDFactory)
register(AttributeFactory)
