import logging
from typing import Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, PrivateAttr

from signals_notebook.common_types import ObjectType
from signals_notebook.entities.plates.cell import PlateCell

log = logging.getLogger(__name__)


class PlateRow(BaseModel):
    id: Optional[UUID] = Field(allow_mutation=False, default=None)
    type: Literal[ObjectType.PLATE_ROW] = Field(allow_mutation=False, default=ObjectType.ADT_ROW)
    cells: List[PlateCell]
    _cells_dict: Dict[Union[UUID, str], PlateCell] = PrivateAttr(default={})

    def __init__(self, **data):
        super().__init__(**data)

        for cell in self.cells:
            self._cells_dict[cell.id] = cell
            self._cells_dict[cell.name] = cell

    class Config:
        validate_assignment = True

    def __getitem__(self, index: Union[int, str, UUID]) -> PlateCell:
        if isinstance(index, int):
            return self.cells[index]

        if isinstance(index, str):
            if index in self._cells_dict:
                return self._cells_dict[index]

            try:
                if UUID(index) in self._cells_dict:
                    return self._cells_dict[UUID(index)]
            except ValueError:
                pass

        if isinstance(index, UUID):
            return self._cells_dict[index]

        raise IndexError('Invalid index')

    def __iter__(self):
        return self.cells.__iter__()
