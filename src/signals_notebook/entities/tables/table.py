import cgi
import json
import logging
from enum import Enum
from typing import Any, cast, Dict, List, Literal, Optional, Union
from uuid import UUID

import pandas as pd
from pydantic import Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import DataList, EntityType, File, Response, ResponseData
from signals_notebook.entities import Entity, EntityStore
from signals_notebook.entities.container import Container
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


class Table(Entity):
    class ContentType(str, Enum):
        JSON = 'application/json'
        CSV = 'text/csv'

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
            use_labels: use cells names

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

    def get_content(self, content_type: str = ContentType.CSV.value) -> File:
        """Get Table content

        Args:
            content_type: Export resource format

        Returns:

        """
        self.ContentType(content_type)
        if content_type == self.ContentType.JSON.value:
            rows = []
            for item in self:
                row = {}
                for cell in item:
                    row[cell.name] = cell.content.dict()
                rows.append(row)
            return File(
                name=f'{self.name}.json',
                content=json.dumps({'data': rows}, default=str).encode('utf-8'),
                content_type=content_type,
            )

        api = SignalsNotebookApi.get_default_api()
        log.debug('Get content for: %s| %s', self.__class__.__name__, self.eid)

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.eid, 'export'),
            params={
                'format': None,
            },
        )

        content_disposition = response.headers.get('content-disposition', '')
        _, params = cgi.parse_header(content_disposition)

        return File(
            name=params['filename'],
            content=response.content,
            content_type=response.headers.get('content-type'),
        )

    @classmethod
    def create(
        cls,
        *,
        container: Container,
        name: str,
        content: List[Dict[str, CellContentDict]] = None,
        template: str = None,
        digest: str = None,
        force: bool = True,
    ) -> Entity:
        """Create Table Entity

        Args:
            container: Container where create new Table
            name: file name
            content: Table content
            template: template for table creation
            digest: Indicate digest of entity. It is used to avoid conflict while concurrent editing.
            force: Force to post attachment

        Returns:
            Table
        """
        log.debug('Create Table: %s...', cls.__name__)
        if template:
            api = SignalsNotebookApi.get_default_api()
            request = {
                'data': {
                    'type': EntityType.GRID,
                    'attributes': {'name': name},
                    'relationships': {
                        'ancestors': {'data': [{'type': EntityType.EXPERIMENT, 'id': container.eid}]},
                        'template': {'data': {'type': EntityType.GRID, 'id': template}},
                    },
                }
            }

            response = api.call(
                method='POST',
                path=(cls._get_endpoint(),),
                params={
                    'digest': digest,
                    'force': json.dumps(force),
                },
                json=request,
            )
            result = TableResponse(**response.json())
            table = cast(ResponseData, result.data).body
            log.debug('Entity: %s was created.', cls.__name__)
            if content:
                for row in content:
                    table.add_row(row)
                table.save()
            return table

        log.debug('There is no needful template. Table will be uploaded as *.csv File...')
        log.debug('Create table: %s with name: %s in Container: %s', cls.__name__, name, container.eid)
        return container.add_child(
            name=name,
            content=json.dumps({'data': content}, default=str).encode('utf-8'),
            content_type=cls.ContentType.JSON,
            force=force,
        )

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

    def dump(self, base_path: str, fs_handler: FSHandler, alias: Optional[List[str]] = None) -> None:
        """Dump Table entity

        Args:
            base_path: content path where create dump
            fs_handler: FSHandler
            alias: Backup alias

        Returns:

        """
        log.debug('Dumping table: %s with name: %s...', self.eid, self.name)

        content = self.get_content(content_type=self.ContentType.JSON)
        column_definitions = self.get_column_definitions_list()

        metadata = {
            'file_name': content.name,
            'content_type': content.content_type,
            'columns': [item.title for item in column_definitions],
            **{k: v for k, v in self.dict().items() if k in ('name', 'description', 'eid')},
        }
        fs_handler.write(
            fs_handler.join_path(base_path, self.eid, 'metadata.json'),
            json.dumps(metadata, default=str),
            base_alias=alias + [self.name, '__Metadata'] if alias else None,
        )
        file_name = content.name
        data = content.content
        fs_handler.write(
            fs_handler.join_path(base_path, self.eid, file_name),
            data,
            base_alias=alias + [self.name, file_name] if alias else None,
        )
        log.debug('Table: %s was dumped successfully', self.eid, self.name)

    @classmethod
    def load(cls, path: str, fs_handler: FSHandler, parent: Container) -> None:
        """Load Table entity

        Args:
            path: content path
            fs_handler: FSHandler
            parent: Container where load Table entity

        Returns:

        """
        cls._load(path, fs_handler, parent)

    @classmethod
    def _load(cls, path: str, fs_handler: FSHandler, parent: Any) -> None:
        log.debug('Loading table from dump...')
        metadata_path = fs_handler.join_path(path, 'metadata.json')
        metadata = json.loads(fs_handler.read(metadata_path))
        content_path = fs_handler.join_path(path, metadata['file_name'])
        content_bytes = fs_handler.read(content_path)
        content = json.loads(content_bytes)
        rows = content['data']
        column_definitions = metadata.get('columns')
        templates = EntityStore.get_list(
            include_types=[EntityType.GRID], include_options=[EntityStore.IncludeOptions.TEMPLATE]
        )

        file_creation = True
        for item in templates:
            template = cast('Table', item)
            template_column_definitions = template.get_column_definitions_list()
            template_columns = [item.title for item in template_column_definitions]
            if set(template_columns) == set(column_definitions):
                file_creation = False
                cls.create(
                    container=parent,
                    name=metadata['name'],
                    template=template.eid,
                    content=rows,
                )
                break

        if file_creation:
            cls.create(container=parent, name=metadata['name'], content=rows, force=True)
        log.debug('Table was loaded to Container: %s', parent.eid)

    @classmethod
    def dump_templates(cls, base_path: str, fs_handler: FSHandler) -> None:
        """Dump Table templates

        Args:
            base_path: content path where create templates dump
            fs_handler: FSHandler

        Returns:

        """
        from signals_notebook.entities import EntityStore

        entity_type = cls._get_entity_type()

        templates = EntityStore.get_list(
            include_types=[entity_type], include_options=[EntityStore.IncludeOptions.TEMPLATE]
        )

        try:
            for item in templates:
                template = cast('Table', item)
                content = template.get_content(content_type=cls.ContentType.JSON)
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
                    ('Templates', entity_type.value, template.name),
                )
        except TypeError:
            pass


class TableResponse(Response[Table]):
    pass
