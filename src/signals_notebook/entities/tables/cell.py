from datetime import datetime
from enum import Enum
from typing import cast, Generic, List, Literal, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field, PrivateAttr
from pydantic.generics import GenericModel

from signals_notebook.entities import Entity
from signals_notebook.entities.entity_store import EntityStore
from signals_notebook.types import EID, EntityType, ObjectType

CellContentType = TypeVar('CellContentType')


class ColumnDataType(str, Enum):
    NUMBER = 'number'
    INTEGER = 'integer'
    DATE_TIME = 'datetime'
    TEXT = 'text'
    LIST = 'list'
    MULTI_SELECT = 'multiSelect'
    ATTRIBUTE_LIST = 'attributeList'
    AUTOTEXT_LIST = 'autotextList'
    BOOLEAN = 'boolean'
    UNIT = 'unit'
    LINK = 'link'
    EXTERNAL_LINK = 'externalLink'


class ColumnDefinition(BaseModel):
    key: UUID
    title: str
    type: ColumnDataType
    is_external_key: Optional[bool] = Field(alias='isExternalKey', default=None)
    is_user_defined: Optional[bool] = Field(alias='isUserDefined', default=None)
    saved: Optional[bool] = Field(default=None)
    read_only: bool = Field(default=True, alias='readOnly')

    class Config:
        frozen = True


class AttributeListColumnDefinition(ColumnDefinition):
    type: Literal[ColumnDataType.ATTRIBUTE_LIST]
    options: List[str]
    attribute_list_eid: EID = Field(alias='attributeListEid')
    multi_select: bool = Field(alias='multiSelect')


class AutotextListColumnDefinition(ColumnDefinition):
    type: Literal[ColumnDataType.AUTOTEXT_LIST]
    options: List[str]
    autotext_list_eid: EID = Field(alias='autotextListEid')


class ListColumnDefinition(ColumnDefinition):
    type: Literal[ColumnDataType.LIST]
    options: List[str]


class MultiSelectColumnDefinition(ColumnDefinition):
    type: Literal[ColumnDataType.MULTI_SELECT]
    options: List[str]


class UnitColumnDefinition(ColumnDefinition):
    type: Literal[ColumnDataType.UNIT]
    measure: str
    default_unit: str = Field(alias='defaultUnit')


ColumnDefinitionClasses = Union[
    AttributeListColumnDefinition,
    AutotextListColumnDefinition,
    ListColumnDefinition,
    MultiSelectColumnDefinition,
    UnitColumnDefinition,
    ColumnDefinition,  # must be the last
]


class ColumnDefinitions(BaseModel):
    id: EID
    type: Literal[ObjectType.COLUMN_DEFINITIONS]
    columns: List[ColumnDefinitionClasses]

    class Config:
        frozen = True


class CellContent(GenericModel, Generic[CellContentType]):
    value: CellContentType
    values: Optional[List[CellContentType]] = None
    type: Optional[EntityType] = None
    display: Optional[str] = None

    class Config:
        validate_assignment = True


class UpdateCellRequest(GenericModel, Generic[CellContentType]):
    key: UUID
    content: CellContent[CellContentType]


class Cell(GenericModel, Generic[CellContentType]):
    id: UUID = Field(allow_mutation=False, alias='key')
    type: ColumnDataType = Field(allow_mutation=False)
    name: str = Field(allow_mutation=False)
    content: CellContent[CellContentType]
    _changed: bool = PrivateAttr(default=False)

    class Config:
        validate_assignment = True

    @property
    def value(self) -> Union[CellContentType, List[CellContentType]]:
        return self.content.values or self.content.value

    def set_value(self, new_value: Union[CellContentType, List[CellContentType]]) -> None:
        if isinstance(new_value, List):
            self.content.value = cast(CellContentType, ','.join(map(str, new_value)))
            self.content.values = new_value
        else:
            self.content.value = new_value
        self._changed = True

    @property
    def is_changed(self) -> bool:
        return self._changed

    @property
    def display(self) -> str:
        return self.content.display or ''

    @property
    def update_request(self) -> Optional[UpdateCellRequest[CellContentType]]:
        return UpdateCellRequest[CellContentType](key=self.id, content=self.content) if self._changed else None


class TextCell(Cell[str]):
    type: Literal[ColumnDataType.TEXT] = Field(allow_mutation=False)


class NumberCell(Cell[float]):
    type: Literal[ColumnDataType.NUMBER] = Field(allow_mutation=False)


class IntegerCell(Cell[int]):
    type: Literal[ColumnDataType.INTEGER] = Field(allow_mutation=False)


class BooleanCell(Cell[bool]):
    type: Literal[ColumnDataType.BOOLEAN] = Field(allow_mutation=False)


class DateTimeCell(Cell[datetime]):
    type: Literal[ColumnDataType.DATE_TIME] = Field(allow_mutation=False)


class ExternalLink(Cell[str]):
    type: Literal[ColumnDataType.EXTERNAL_LINK] = Field(allow_mutation=False)


class LinkCell(Cell[EID]):
    type: Literal[ColumnDataType.LINK] = Field(allow_mutation=False)

    @property
    def entity(self) -> Entity:
        return EntityStore.get(self.content.value)


class UnitCell(Cell[float]):
    type: Literal[ColumnDataType.UNIT] = Field(allow_mutation=False)


class MultiSelectCell(Cell[str]):
    type: Literal[ColumnDataType.MULTI_SELECT] = Field(allow_mutation=False)


class AttributeListCell(Cell[str]):
    type: Literal[ColumnDataType.ATTRIBUTE_LIST] = Field(allow_mutation=False)


class ListCell(Cell[str]):
    type: Literal[ColumnDataType.LIST] = Field(allow_mutation=False)


class AutotextListCell(Cell[str]):
    type: Literal[ColumnDataType.AUTOTEXT_LIST] = Field(allow_mutation=False)


GenericCell = Union[
    AttributeListCell,
    AutotextListCell,
    BooleanCell,
    DateTimeCell,
    ExternalLink,
    IntegerCell,
    LinkCell,
    ListCell,
    MultiSelectCell,
    NumberCell,
    TextCell,
    UnitCell,
    Cell,  # must be the last
]
