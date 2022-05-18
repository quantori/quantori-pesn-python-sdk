import json
from typing import Any, cast, Dict, List, Literal, Union
from uuid import UUID

import pandas as pd
from pydantic import Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import DataList, EntityType, Response, ResponseData
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.entities.tables.cell import CellContentDict, ColumnDefinitions, GenericColumnDefinition, Cell
from signals_notebook.entities.tables.row import ChangeRowRequest, Row
from signals_notebook.jinja_env import env


class TableDataResponse(Response[Row]):
    pass


class ColumnDefinitionsResponse(Response[ColumnDefinitions]):
    pass


class ChangeTableDataRequest(DataList[ChangeRowRequest]):
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
            params={
                'value': 'normalized',
            },
        )

        result = TableDataResponse(**response.json())

        self._rows = []
        self._rows_by_id = {}
        for item in result.data:
            row = cast(Row, cast(ResponseData, item))
            assert row.id

            self._rows.append(row)
            self._rows_by_id[row.id] = row

    def get_table_content(self):
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_adt_endpoint(), self.eid),
        )
        result = TableDataResponse(**response.json())

        return cast(ResponseData, result.data)

    def get_column_definitions_list(self) -> List[GenericColumnDefinition]:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(method='GET', path=(self._get_adt_endpoint(), self.eid, '_column'))

        result = ColumnDefinitionsResponse(**response.json())

        return cast(ResponseData, result.data).body.columns

    def get_column_definitions_map(self) -> Dict[str, GenericColumnDefinition]:
        column_definitions = self.get_column_definitions_list()
        column_definitions_map: Dict[str, GenericColumnDefinition] = {}

        for column_definition in column_definitions:
            column_definitions_map[str(column_definition.key)] = column_definition
            column_definitions_map[column_definition.title] = column_definition

        return column_definitions_map

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
        if not self._rows:
            self._reload_data()

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

        self._reload_data()

    def add_row(self, data: Dict[str, CellContentDict]) -> None:
        column_definitions_map = self.get_column_definitions_map()

        prepared_data: List[Dict[str, Any]] = []
        for key, value in data.items():
            column_definition = column_definitions_map.get(key)
            if not column_definition:
                continue

            prepared_data.append(
                {
                    'key': column_definition.key,
                    'type': column_definition.type,
                    'name': column_definition.title,
                    'content': value,
                }
            )

        row = Row(cells=prepared_data)
        self._rows.append(row)

    def save(self, force: bool = True) -> None:
        super().save(force)

        row_requests: List[ChangeRowRequest] = []
        for row in self._rows:
            row_request = row.get_change_request()
            if row_request:
                row_requests.append(row_request)

        if not row_requests:
            return

        request = ChangeTableDataRequest(data=row_requests)
        api = SignalsNotebookApi.get_default_api()

        api.call(
            method='PATCH',
            path=(self._get_adt_endpoint(), self.eid),
            params={
                'digest': None if force else self.digest,
                'force': json.dumps(force),
            },
            data=request.json(exclude_none=True, by_alias=True),
        )

        self._reload_data()

    def get_html(self, template_name: str = 'table.html') -> str:
        rows = []

        table_head = []
        for column_definition in self.get_column_definitions_list():
            table_head.append(column_definition.title)

        for elem in self.get_table_content():  # TODO: refactor this. Add null content value for Nullable cells
            row = []
            for item in elem.body:
                row.append(item.content.value)

            rows.append(row)

        template = env.get_template(template_name)

        return template.render(name=self.name, table_head=table_head, rows=rows)
