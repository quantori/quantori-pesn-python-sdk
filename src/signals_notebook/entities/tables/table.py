import json
import logging
from typing import Any, cast, Dict, List, Literal, Union
from uuid import UUID

import pandas as pd
from pydantic import Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import DataList, EntityType, Response, ResponseData
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.entities.tables.cell import Cell, CellContentDict, ColumnDefinitions, GenericColumnDefinition
from signals_notebook.entities.tables.row import ChangeRowRequest, Row
from signals_notebook.jinja_env import env
from signals_notebook.utils import FSHandler

log = logging.getLogger(__name__)


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
    _template_name = 'table.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.GRID

    @classmethod
    def _get_adt_endpoint(cls) -> str:
        return 'adt'

    def _reload_data(self) -> None:
        api = SignalsNotebookApi.get_default_api()
        log.debug('Reloading data in Table: %s...', self.eid)

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
            row = cast(Row, cast(ResponseData, item).body)
            assert row.id

            self._rows.append(row)
            self._rows_by_id[row.id] = row
        log.debug('Data in Table: %s were reloaded', self.eid)

    def get_column_definitions_list(self) -> List[GenericColumnDefinition]:
        """Fetch column definitions

        Returns:
            List[GenericColumnDefinition]
        """
        api = SignalsNotebookApi.get_default_api()

        response = api.call(method='GET', path=(self._get_adt_endpoint(), self.eid, '_column'))

        result = ColumnDefinitionsResponse(**response.json())

        return cast(ResponseData, result.data).body.columns

    def get_column_definitions_map(self) -> Dict[str, GenericColumnDefinition]:
        """Get column definitions as a dictionary

        Returns:
            Dict[str, GenericColumnDefinition]
        """
        column_definitions = self.get_column_definitions_list()
        column_definitions_map: Dict[str, GenericColumnDefinition] = {}

        for column_definition in column_definitions:
            column_definitions_map[str(column_definition.key)] = column_definition
            column_definitions_map[column_definition.title] = column_definition

        return column_definitions_map

    def as_dataframe(self, use_labels: bool = True) -> pd.DataFrame:
        """Get as data table

        Args:
            use_labels: use cels names

        Returns:
            pd.DataFrame
        """
        if not self._rows:
            self._reload_data()

        data = []
        index = []
        for row in self._rows:
            index.append(row.id)
            data.append(row.get_values(use_labels))

        return pd.DataFrame(data=data, index=index)

    def as_raw_data(self, use_labels: bool = True) -> List[Dict[str, Any]]:
        """Get as a list of dictionaries

        Args:
            use_labels: use cels names

        Returns:

        """
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

        log.exception('IndexError were caught. Invalid index')
        raise IndexError('Invalid index')

    def __iter__(self):
        if not self._rows:
            self._reload_data()

        return self._rows.__iter__()

    def delete_row_by_id(self, row_id: Union[str, UUID], digest: str = None, force: bool = True) -> None:
        """

        Args:
            row_id: id of the row
            digest: Indicate digest of entity. It is used to avoid conflict while concurrent editing.
            If the parameter 'force' is true, this parameter is optional.
            If the parameter 'force' is false, this parameter is required.
            force: Force to update properties without digest check.

        Returns:

        """
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

        log.debug('Row %s was deleted', row_id)
        self._reload_data()

    def add_row(self, data: Dict[str, CellContentDict]) -> None:
        """Add row in the table

        Args:
            data: Cells to add in the row

        Returns:

        """
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
        log.debug('Row: %s was added to Table', row)

    def save(self, force: bool = True) -> None:
        """Save all changes in the table

        Args:
            force: Force to update properties without digest check.

        Returns:

        """
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

    def get(self, value: Union[str, UUID], default: Any = None) -> Union[Row, Any]:
        """Get Row

        Args:
            value: name of id of Row
            default: default value if it doens't exist

        Returns:
            Union[Row, Any]
        """
        try:
            return self[value]
        except KeyError:
            log.debug('KeyError were caught. Default value returned')
            return default

    def get_html(self) -> str:
        """Get in HTML format

        Returns:
            Rendered template as a string
        """

        rows = []
        column_definitions = self.get_column_definitions_list()

        table_head = []
        for column_definition in column_definitions:
            table_head.append(column_definition.title)

        for row in self:
            reformatted_row = {}

            for column_definition in column_definitions:
                cell = cast(Row, row).get(column_definition.key, None)
                cell = cast(Cell, cell)
                reformatted_row[column_definition.title] = '' if cell is None else (cell.display or cell.value)

            rows.append(reformatted_row)

        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(name=self.name, table_head=table_head, rows=rows)

    @classmethod
    def dump_templates(cls, base_path: str, fs_handler: FSHandler) -> None:
        from signals_notebook.entities import EntityStore

        entity_type = cls._get_entity_type()

        templates = EntityStore.get_list(
            include_types=[entity_type], include_options=[EntityStore.IncludeOptions.TEMPLATE]
        )

        try:
            for item in templates:
                template = cast('Table', item)
                content = template._get_content()
                column_definitions = template.get_column_definitions_list()
                metadata = {
                    'file_name': content.name,
                    'content_type': content.content_type,
                    'columns': [item.title for item in column_definitions],
                    **{k: v for k, v in template.dict().items() if k in ('name', 'description', 'eid')},
                }
                fs_handler.write(
                    fs_handler.join_path(base_path, 'templates', entity_type, f'metadata_{template.name}.json'),
                    json.dumps(metadata),
                )
        except TypeError:
            pass
