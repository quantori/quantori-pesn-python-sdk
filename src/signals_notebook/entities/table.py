import json
from enum import Enum
from operator import attrgetter
from typing import Any, cast, Dict, Generator, List, Literal, Optional, Tuple, Type, Union
from uuid import UUID

import pandas as pd
from pydantic import BaseModel, Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.types import EID, EntitySubtype, EntityType, Response, ResponseData


class ColumnDataType(str, Enum):
    NUMBER = 'number'
    DATE = 'date'
    TEXT = 'text'
    LIST = 'list'
    MULTISELECT = 'multiSelect'
    ATTRIBUTE_LIST = 'attributeList'
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
    read_only: bool = Field(default=True, alias='readOnly')

    class Config:
        frozen = True


class AttributeListColumnDefinition(ColumnDefinition):
    type: Literal[ColumnDataType.ATTRIBUTE_LIST]
    options: List[str]
    attribute_list_eid: EID = Field(alias='attributeListEid')
    multi_select: bool = Field(alias='multiSelect')


ColumnDefinitionClasses = Union[AttributeListColumnDefinition, ColumnDefinition]


class ColumnDefinitions(BaseModel):
    id: EID
    type: Literal[EntityType.COLUMN_DEFINITIONS]
    columns: List[ColumnDefinitionClasses]

    class Config:
        frozen = True


class _Content(BaseModel):
    value: Any
    type: Optional[EntitySubtype] = None
    display: Optional[str] = None


class Cell(BaseModel):
    id: UUID = Field(allow_mutation=False, alias='key')
    type: ColumnDataType = Field(allow_mutation=False)
    name: str = Field(allow_mutation=False)
    content: _Content

    class Config:
        validate_assignment = True

    @property
    def value(self) -> Any:
        return self.content.value


class Row(BaseModel):
    id: UUID = Field(allow_mutation=False)
    type: Literal[EntityType.ADT_ROW] = Field(allow_mutation=False)
    cells: List[Cell]
    _cells_dict: Dict[Union[UUID, str], Cell] = PrivateAttr(default={})
    _table: Optional['Table'] = PrivateAttr(default=None)

    class Config:
        validate_assignment = True

    def __init__(self, **data):
        super().__init__(**data)

        for cell in self.cells:
            self._cells_dict[cell.id] = cell
            self._cells_dict[cell.name] = cell

    @property
    def table(self) -> Optional['Table']:
        return self._table

    def set_table(self, table_instance: 'Table') -> None:
        self._table = table_instance

    def get_values(self, use_labels: bool = True) -> Dict[str, Any]:
        key_getter = attrgetter('name') if use_labels else attrgetter('key')
        return {key_getter(cell): cell.value for cell in self.cells}

    def __getitem__(self, index: Union[int, str, UUID]) -> Cell:
        if isinstance(index, int):
            return self.cells[index]

        if isinstance(index, str):
            if index in self._cells_dict:
                return self._cells_dict[index]
            return self._cells_dict[UUID(index)]

        if isinstance(index, UUID):
            return self._cells_dict[index]

        raise IndexError('Invalid index type')

    def delete(self) -> None:
        assert self.table
        self.table.delete_row_by_id(self.id)


class TableDataResponse(Response[Row]):
    pass


class ColumnDefinitionsResponse(Response[ColumnDefinitions]):
    pass


class Table(ContentfulEntity):
    type: Literal[EntitySubtype.GRID] = Field(allow_mutation=False)
    _rows: List[Row] = PrivateAttr(default=[])
    _rows_by_id: Dict[UUID, Row] = PrivateAttr(default={})

    @classmethod
    def _get_subtype(cls) -> EntitySubtype:
        return EntitySubtype.GRID

    @classmethod
    def _get_adt_endpoint(cls) -> str:
        return 'adt'

    def _reload_data(self) -> None:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_adt_endpoint(), self.eid),
        )

        result = TableDataResponse(**response.json())

        self._rows = []
        self._rows_by_id = {}
        for item in result.data:
            row = cast(Row, cast(ResponseData, item).body)
            row.set_table(self)
            self._rows.append(row)
            self._rows_by_id[row.id] = row

    def get_column_definitions(self) -> List[ColumnDefinition]:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_adt_endpoint(), self.eid, '_column')
        )

        result = ColumnDefinitionsResponse(**response.json())

        return cast(ResponseData, result.data).body.columns

    def as_dataframe(self, use_labels: bool = True) -> pd.DataFrame:
        if not self._rows:
            self._reload_data()

        data = []
        index = []
        for row in self._rows:
            index.append(row.id)
            data.append(row.get_values(use_labels))

        return pd.DataFrame(data=data, index=index)

    def as_raw_data(self, use_labels: bool = True) -> List[Dict[str, Any]]:
        if not self._rows:
            self._reload_data()

        data = []
        for row in self._rows:
            data.append(row.get_values(use_labels))

        return data

    def __getitem__(self, index: Union[int, str, UUID]) -> Row:
        if not self._rows:
            self._reload_data()

        if isinstance(index, int):
            return self._rows[index]

        if isinstance(index, str):
            return self._rows_by_id[UUID(index)]

        if isinstance(index, UUID):
            return self._rows_by_id[index]

        raise IndexError('Invalid index type')

    def __iter__(self):
        return self._rows.__iter__()

    def delete_row_by_id(self, row_id: Union[str, UUID], digest: str = None, force: bool = True) -> None:
        if isinstance(row_id, UUID):
            _row_id = row_id.hex
        else:
            _row_id = row_id

        api = SignalsNotebookApi.get_default_api()

        api.call(
            method='DELETE',
            path=(self._get_adt_endpoint(), self.eid, _row_id),
            params={
                'digest': digest,
                'force': json.dumps(force),
            },
        )

