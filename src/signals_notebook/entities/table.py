from collections import defaultdict
from enum import Enum
from typing import Any, Dict, List, Literal
from uuid import UUID

import pandas as pd
from pydantic import BaseModel, Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.types import EntitySubtype, EntityType, Response


class CellValueType(str, Enum):
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


class _Content(BaseModel):
    value: Any


class Cell(BaseModel):
    key: UUID = Field(allow_mutation=False)
    type: CellValueType = Field(allow_mutation=False)
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

    @property
    def values(self) -> Dict[str, Any]:
        return {cell.name: cell.value for cell in self.cells}


class TableResponse(Response[Row]):
    pass


class Table(ContentfulEntity):
    type: Literal[EntitySubtype.GRID] = Field(allow_mutation=False)

    @classmethod
    def _get_subtype(cls) -> EntitySubtype:
        return EntitySubtype.GRID

    @classmethod
    def _get_adt_endpoint(cls) -> str:
        return 'adt'

    def get_dataframe(self) -> pd.DataFrame:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_adt_endpoint(), self.eid),
        )

        result = TableResponse(**response.json())

        data = []
        index = []
        for response_data in result.data:
            row = response_data.body
            index.append(row.id)
            data.append(row.values)

        return pd.DataFrame(data=data, index=index)
