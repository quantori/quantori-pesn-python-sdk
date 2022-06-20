from signals_notebook.common_types import EntityType
from signals_notebook.entities import Table
from tests.entities.factories import EntityFactory


class TableFactory(EntityFactory):
    class Meta:
        model = Table

    type = EntityType.GRID
