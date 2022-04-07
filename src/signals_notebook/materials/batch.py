from typing import Literal

from pydantic import Field

from signals_notebook.common_types import MaterialType
from signals_notebook.materials.material import Material


class Batch(Material):
    type: Literal[MaterialType.BATCH] = Field(allow_mutation=False, default=MaterialType.BATCH)
