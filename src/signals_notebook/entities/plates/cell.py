from enum import Enum
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import Field
from pydantic.generics import GenericModel


CellContentType = TypeVar('CellContentType')


class ColumnDataType(str, Enum):
    NUMBER = 'NUMBER'
    INTEGER = 'INTEGER'
    DATE_TIME = 'DATETIME'
    TEXT = 'TEXT'
    LIST = 'LIST'
    MULTI_SELECT = 'MULTI_SELECT'
    ATTRIBUTE_LIST = 'ATTRIBUTE_LIST'
    AUTOTEXT_LIST = 'AUTOTEXT_LIST'
    BOOLEAN = 'BOOLEAN'
    UNIT = 'UNIT'
    LINK = 'LINK'
    EXTERNAL_LINK = 'EXTERNAL_LINK'


class CellContent(GenericModel, Generic[CellContentType]):
    user: Optional[str]
    value: Optional[CellContentType] = None
    values: Optional[List[CellContentType]] = None

    class Config:
        validate_assignment = True


class PlateCell(GenericModel, Generic[CellContentType]):
    id: UUID = Field(allow_mutation=False, alias='key')
    type: ColumnDataType = Field(allow_mutation=False)
    name: str = Field(allow_mutation=False)
    content: CellContent[CellContentType]

    class Config:
        validate_assignment = True
