from typing import Literal

from pydantic import Field

from signals_notebook.materials.material import Material
from signals_notebook.types import MaterialType


class Batch(Material):
    type: Literal[MaterialType.BATCH] = Field(allow_mutation=False, default=MaterialType.BATCH)

