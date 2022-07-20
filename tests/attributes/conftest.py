from pytest_factoryboy import register

from tests.attributes.factories import AttributeFactory, AttributeOptionFactory, AttrIDFactory

register(AttrIDFactory)
register(AttributeFactory)
register(AttributeOptionFactory)
