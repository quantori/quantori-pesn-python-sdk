from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ColumnDataType(str, Enum):
    NUMBER = 'number'
    INTEGER = 'integer'
    TEXT = 'text'
    HTML = 'html'
    BOOLEAN = 'boolean'
    UNIT = 'unit'
    LINK = 'link'


class ColumnDefinition(BaseModel):
    key: str
    title: str
    type: ColumnDataType
    measure: Optional[str]
    read_only: Optional[bool] = Field(default=None, alias='readOnly')
    hidden: Optional[bool] = Field(default=None)
    hideable: Optional[bool] = Field(default=None)
    prevent_edit_identity: Optional[bool] = Field(default=None, alias='preventEditIdentity')
    prevent_toggle_read_only: Optional[bool] = Field(default=None, alias='preventToggleReadOnly')

    class Config:
        frozen = True


class ColumnDefinitions(BaseModel):
    reactants: Optional[list[ColumnDefinition]]
    products: Optional[list[ColumnDefinition]]
    solvents: Optional[list[ColumnDefinition]]
    conditions: Optional[list[ColumnDefinition]]

    class Config:
        frozen = True
