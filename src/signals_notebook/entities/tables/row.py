import logging
from enum import Enum
from operator import attrgetter
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, PrivateAttr

from signals_notebook.common_types import ObjectType
from signals_notebook.entities.tables.cell import Cell, GenericCell, UpdateCellRequest

log = logging.getLogger(__name__)


class RowAction(str, Enum):
    UPDATE = 'update'
    CREATE = 'create'
    DELETE = 'delete'


class DeleteRowActionBody(BaseModel):
    action: Literal[RowAction.DELETE] = Field(allow_mutation=False, default=RowAction.DELETE)

    class Config:
        validate_assignment = True


class UpdateRowActionBody(BaseModel):
    action: Literal[RowAction.UPDATE] = Field(allow_mutation=False, default=RowAction.UPDATE)
    cells: List[UpdateCellRequest]

    class Config:
        validate_assignment = True


class CreateRowActionBody(BaseModel):
    action: Literal[RowAction.CREATE] = Field(allow_mutation=False, default=RowAction.CREATE)
    cells: List[UpdateCellRequest]

    class Config:
        validate_assignment = True


class ChangeRowRequest(BaseModel):
    type: Literal[ObjectType.ADT_ROW] = Field(allow_mutation=False, default=ObjectType.ADT_ROW)

    class Config:
        validate_assignment = True


class DeleteRowRequest(ChangeRowRequest):
    id: UUID
    body: DeleteRowActionBody = Field(alias='attributes', default_factory=DeleteRowActionBody)


class UpdateRowRequest(ChangeRowRequest):
    id: UUID
    body: UpdateRowActionBody = Field(alias='attributes')


class CreateRowRequest(ChangeRowRequest):
    body: CreateRowActionBody = Field(alias='attributes')


class Row(BaseModel):
    id: Optional[UUID] = Field(allow_mutation=False, default=None)
    type: Literal[ObjectType.ADT_ROW] = Field(allow_mutation=False, default=ObjectType.ADT_ROW)
    cells: List[GenericCell]
    _cells_dict: Dict[Union[UUID, str], GenericCell] = PrivateAttr(default={})
    _deleted: bool = PrivateAttr(default=False)

    class Config:
        validate_assignment = True

    def __init__(self, **data):
        super().__init__(**data)

        for cell in self.cells:
            self._cells_dict[cell.id] = cell
            self._cells_dict[cell.name] = cell

    def get(self, value: Union[str, UUID], default: Any = None) -> Union[Cell, Any]:
        """Get one of the GenericCell objects by value

        Args:
            value: key to get one of the GenericCell objects
            default: default value if key doesn't exist

        Returns:
            Union[Cell, Any]
        """
        try:
            return self[value]
        except KeyError:
            log.debug('KeyError were caught. Default value returned')
            return default

    @property
    def is_deleted(self) -> bool:
        """Get is_deleted field

        Returns:
            bool: True/False
        """
        return self._deleted

    @property
    def is_changed(self) -> bool:
        """Get is_changed field

        Returns:
            bool: True/False
        """
        return any([cell.is_changed for cell in self.cells])

    @property
    def is_new(self) -> bool:
        """Check if id field exists

        Returns:
            bool: True/False
        """
        return self.id is None

    def get_values(self, use_labels: bool = True) -> Dict[str, Any]:
        """Get row values

        Args:
            use_labels: use cels names

        Returns:
            Dict[str, Any]
        """
        key_getter = attrgetter('name') if use_labels else attrgetter('key')
        return {key_getter(cell): cell.value for cell in self.cells}

    def __getitem__(self, index: Union[int, str, UUID]) -> GenericCell:
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

    def delete(self) -> None:
        """Delete Row

        Returns:

        """
        self._deleted = True

    def get_change_request(self) -> Optional[ChangeRowRequest]:
        """Get ChangeRowRequest depending on Row status

        Returns:
            Optional[ChangeRowRequest]
        """
        if self.is_deleted:
            return DeleteRowRequest(id=self.id)

        if self.is_changed:
            return UpdateRowRequest(
                id=self.id,
                attributes=UpdateRowActionBody(cells=[cell.update_request for cell in self.cells if cell.is_changed]),
            )

        if self.is_new:
            return CreateRowRequest(attributes=CreateRowActionBody(cells=[cell.update_request for cell in self.cells]))

        return None
