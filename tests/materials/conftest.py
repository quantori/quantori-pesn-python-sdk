from pytest_factoryboy import register

from tests.materials.factories import AssetFactory, BatchFactory, LibraryFactory, MIDFactory

register(MIDFactory)
register(LibraryFactory)
register(AssetFactory)
register(BatchFactory)
