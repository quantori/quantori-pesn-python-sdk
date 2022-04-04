from entities.factories import EntityFactory
from signals_notebook.common_types import EntityType
from signals_notebook.entities import Table


class TableFactory(EntityFactory):
    class Meta:
        model = Table

    type = EntityType.GRID
