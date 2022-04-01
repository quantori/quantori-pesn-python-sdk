from typing import cast, Literal, TYPE_CHECKING

from pydantic import Field

from signals_notebook.materials.material import Material
from signals_notebook.types import MaterialType, MID

if TYPE_CHECKING:
    from signals_notebook.materials.library import Library


class Batch(Material):
    type: Literal[MaterialType.BATCH] = Field(allow_mutation=False, default=MaterialType.BATCH)

    @property
    def library(self) -> 'Library':
        from signals_notebook.materials.material_store import MaterialStore
        library = MaterialStore.get(MID(f'{MaterialType.LIBRARY}:{self.asset_type_id}'))
        return cast('Library', library)
