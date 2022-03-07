import json
from operator import attrgetter
from typing import Any, cast, Dict, List, Literal, Optional, Union
from uuid import UUID

import pandas as pd
from pydantic import BaseModel, Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.entities.tables.cell import GenericCell, ColumnDefinition, ColumnDefinitions
from signals_notebook.types import EntityType, ObjectType, Response, ResponseData


class Row(BaseModel):
    id: UUID = Field(allow_mutation=False)
    type: Literal[ObjectType.ADT_ROW] = Field(allow_mutation=False)
    cells: List[GenericCell]
    _cells_dict: Dict[Union[UUID, str], GenericCell] = PrivateAttr(default={})
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
        assert self.table
        self.table.delete_row_by_id(self.id)


class TableDataResponse(Response[Row]):
    pass


class ColumnDefinitionsResponse(Response[ColumnDefinitions]):
    pass


class Table(ContentfulEntity):
    type: Literal[EntityType.GRID] = Field(allow_mutation=False)
    _rows: List[Row] = PrivateAttr(default=[])
    _rows_by_id: Dict[UUID, Row] = PrivateAttr(default={})

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.GRID

    @classmethod
    def _get_adt_endpoint(cls) -> str:
        return 'adt'

    def _reload_data(self) -> None:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_adt_endpoint(), self.eid),
        )
        breakpoint()
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

        raise IndexError('Invalid index')

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

