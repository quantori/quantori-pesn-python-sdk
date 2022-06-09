from typing import Generic, List, Optional, TypeVar

from pydantic import PrivateAttr
from pydantic.generics import GenericModel

from signals_notebook.common_types import EID

CellValueType = TypeVar('CellValueType')


class CellPropertyContent(GenericModel, Generic[CellValueType]):
    value: Optional[CellValueType]
    name: Optional[str]
    eid: Optional[EID]
    values: Optional[List[CellValueType]]
    _changed: bool = PrivateAttr(default=False)

    def set_value(self, new_value: CellValueType) -> None:
        self.value = new_value
        self._changed = True

    def set_values(self, new_values: List[CellValueType]) -> None:
        self.values = new_values
        self._changed = True

    def set_name(self, new_name: str) -> None:
        self.name = new_name
        self._changed = True

    @property
    def is_changed(self) -> bool:
        return self._changed


class FieldData(GenericModel, Generic[CellValueType]):
    display: Optional[str]
    value: Optional[CellValueType]
    units: Optional[str]
    eid: Optional[EID]
