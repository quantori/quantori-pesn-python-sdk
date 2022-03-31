from pytest_factoryboy import register

from tests.materials.factories import AssetFactory, MIDFactory

register(MIDFactory)
register(AssetFactory)
