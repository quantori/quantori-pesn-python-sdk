from typing import TypeVar, Generic, Optional, List

from pydantic import PrivateAttr
from pydantic.generics import GenericModel

from signals_notebook.common_types import EntityType, EID

CellContentType = TypeVar('CellContentType')


class CellPropertyBase(GenericModel, Generic[CellContentType]):
    value: Optional[CellContentType]
    type: Optional[EntityType] = None
    name: Optional[str]

    def _set_value(self):
        self._changed = True


class CellPropertyContent(GenericModel, Generic[CellContentType]):
    value: Optional[CellContentType]
    type: Optional[EntityType] = None
    name: Optional[str]
    eid: Optional[EID]
    values: Optional[List[str]]
    _changed: bool = PrivateAttr(default=False)

    def set_value(self, new_value: CellContentType) -> None:
        self.value = new_value
        self._changed = True

    def set_values(self, new_values: List[str]) -> None:
        self.values = new_values
        self._changed = True

    def set_type(self, new_type: EntityType) -> None:
        self.type = new_type
        self._changed = True

    def set_name(self, new_name: str) -> None:
        self.name = new_name
        self._changed = True

    @property
    def changed(self) -> bool:
        return self._changed


class CellPropertyUpdateBody(CellPropertyBase):
    values: Optional[List[str]]
