from collections import defaultdict
from enum import Enum
from operator import attrgetter
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

import pandas as pd
from pydantic import BaseModel, Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.types import EID, EntitySubtype, EntityType, Response


class ColumnDataType(str, Enum):
    NUMBER = 'number'
    DATE = 'date'
    TEXT = 'text'
    LIST = 'list'
    MULTISELECT = 'multiSelect'
    ATTRIBUTELIST = 'attributeList'
    BOOLEAN = 'boolean'
    UNIT = 'unit'
    LINK = 'link'
    EXTERNALLINK = 'externalLink'


class ColumnDefinition(BaseModel):
    key: UUID
    title: str
    type: ColumnDataType
    is_external_key: Optional[bool] = Field(alias='isExternalKey', default=None)
    is_user_defined: Optional[bool] = Field(alias='isUserDefined', default=None)
    saved: Optional[bool] = Field(default=None)

    class Config:
        frozen = True


class ColumnDefinitions(BaseModel):
    id: EID
    type: Literal[EntityType.COLUMN_DEFINITIONS]
    columns: List[ColumnDefinition]

    class Config:
        frozen = True


class _Content(BaseModel):
    value: Any


class Cell(BaseModel):
    key: UUID = Field(allow_mutation=False)
    type: ColumnDataType = Field(allow_mutation=False)
    name: str = Field(allow_mutation=False)
    content: _Content

    class Config:
        validate_assignment = True

    @property
    def value(self) -> Any :
        return self.content.value


class Row(BaseModel):
    id: UUID = Field(allow_mutation=False)
    type: Literal[EntityType.ADT_ROW] = Field(allow_mutation=False)
    cells: List[Cell]

    class Config:
        validate_assignment = True

    def get_values(self, use_labels: bool = True) -> Dict[str, Any]:
        key_getter = attrgetter('name') if use_labels else attrgetter('key')
        return {key_getter(cell): cell.value for cell in self.cells}


class TableDataResponse(Response[Row]):
    pass


class ColumnDefinitionsResponse(Response[ColumnDefinitions]):
    pass


class Table(ContentfulEntity):
    type: Literal[EntitySubtype.GRID] = Field(allow_mutation=False)

    @classmethod
    def _get_subtype(cls) -> EntitySubtype:
        return EntitySubtype.GRID

    @classmethod
    def _get_adt_endpoint(cls) -> str:
        return 'adt'

    def _get_data(self) -> TableDataResponse:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_adt_endpoint(), self.eid),
        )

        return TableDataResponse(**response.json())

    def get_column_definitions(self) -> List[ColumnDefinition]:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_adt_endpoint(), self.eid, '_column')
        )

        result = ColumnDefinitionsResponse(**response.json())

        return result.data.body.columns

    def as_dataframe(self, use_labels: bool=True) -> pd.DataFrame:
        result = self._get_data()

        data = []
        index = []
        for response_data in result.data:
            row = response_data.body
            index.append(row.id)
            data.append(row.get_values(use_labels))

        return pd.DataFrame(data=data, index=index)

    def as_rows(self, use_labels: bool=True) -> List[Dict[str, Any]]:
        result = self._get_data()

        data = []
        for response_data in result.data:
            row = response_data.body
            data.append(row.get_values(use_labels))

        return data
