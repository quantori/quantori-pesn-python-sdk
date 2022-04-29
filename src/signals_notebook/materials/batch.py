from typing import Any, Literal

from pydantic import Field

from signals_notebook.common_types import MaterialType
from signals_notebook.materials.field import FieldContainer
from signals_notebook.materials.material import Material


class Batch(Material):
    type: Literal[MaterialType.BATCH] = Field(allow_mutation=False, default=MaterialType.BATCH)

    def __init__(self, **data: Any):
        fields = data.pop('fields', {})
        super().__init__(**data)

        self._material_fields = FieldContainer(self, self.library.batch_config.fields, **fields)
