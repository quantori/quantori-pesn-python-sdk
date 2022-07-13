from signals_notebook.common_types import EntityType
from signals_notebook.entities import PlateContainer
from tests.entities.factories import EntityFactory


class PlateContainerFactory(EntityFactory):
    class Meta:
        model = PlateContainer

    type = EntityType.PLATE_CONTAINER
