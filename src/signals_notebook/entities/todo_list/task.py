import json
import logging
from typing import cast, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import (
    EntityType,
    Response,
    ResponseData,
)
from signals_notebook.entities import Entity
from signals_notebook.entities.todo_list.cell import TaskCell
from signals_notebook.utils import FSHandler

log = logging.getLogger(__name__)


class TaskCellsResponse(Response[TaskCell]):
    pass


class Task(Entity):
    type: Literal[EntityType.TASK] = Field(allow_mutation=False)
    _cells: List[TaskCell] = PrivateAttr(default=[])
    _cells_by_id: Dict[Union[str, UUID], TaskCell] = PrivateAttr(default={})

    def __getitem__(self, index: Union[int, str, UUID]) -> TaskCell:
        if not self._cells:
            self._reload_cells()

        if isinstance(index, int):
            return self._cells[index]

        if isinstance(index, str):
            try:
                return self._cells_by_id[UUID(index)]
            except ValueError:
                return self._cells_by_id[index]

        if isinstance(index, UUID):
            return self._cells_by_id[index]

        raise IndexError('Invalid index')

    def __iter__(self):
        if not self._cells:
            self._reload_cells()
        return self._cells.__iter__()

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.TASK

    @classmethod
    def _get_tasks_endpoint(cls) -> str:
        return 'tasks'

    def _reload_cells(self) -> None:
        log.debug('Reloading cells in Task: %s...', self.eid)
        self._cells = []
        self._cells_by_id = {}

        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_tasks_endpoint(), self.eid, 'properties'),
            params={'value': 'normalized'},
        )

        result = TaskCellsResponse(**response.json())
        cells = [cast(ResponseData, item).body for item in result.data]

        for item in cells:
            task_cell = cast(TaskCell, item)
            assert task_cell.id

            self._cells.append(task_cell)
            self._cells_by_id[task_cell.id] = task_cell
        log.debug('Cells in Task: %s were reloaded', self.eid)

    def save(self, force: bool = True) -> None:
        """Save all changes in the Task

        Args:
            force: Force to update properties without digest check.

        Returns:

        """
        log.debug('Saving Task: %s...', self.eid)
        api = SignalsNotebookApi.get_default_api()

        request_body = []
        for item in self._cells:
            if item.is_changed:
                request_body.append(item.representation_for_update.dict(exclude_none=True))

        if not request_body:
            return

        api.call(
            method='PATCH',
            path=(self._get_tasks_endpoint(), self.eid, 'properties'),
            params={
                'force': json.dumps(force),
                'value': 'normalized',
            },
            json={
                'data': {'attributes': {'data': request_body}},
            },
        )
        self._reload_cells()
        log.debug('Task: %s was saved successfully', self.eid)

    def dump(
        self, base_path: str, fs_handler: FSHandler, alias: Optional[List[str]] = None
    ) -> None:  # type: ignore[override]
        """Dump Task entity

        Args:
            base_path: content path where create dump
            fs_handler: FSHandler
            alias: Backup alias

        Returns:

        """
        log.debug('Dumping task: %s with name: %s...', self.eid, self.name)

        properties = [item.dict() for item in self]

        metadata = {
            'properties': [item['name'] for item in properties if item['name']],
            'filename': f'{self.name}.json',
            **{k: v for k, v in self.dict().items() if k in ('name', 'description', 'eid')},
        }
        fs_handler.write(
            fs_handler.join_path(base_path, self.eid, 'metadata.json'),
            json.dumps(metadata, default=str),
            base_alias=alias,
        )
        fs_handler.write(
            fs_handler.join_path(base_path, self.eid, f'{self.name}.json'),
            json.dumps({'data': properties}, default=str),
            base_alias=alias,
        )
        log.debug('Task: %s was dumped successfully', self.eid, self.name)

    @classmethod
    def dump_templates(cls, base_path: str, fs_handler: FSHandler) -> None:
        """Dump Task templates

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
                template = cast('Task', item)
                properties = [item for item in template]
                metadata = {
                    'properties': [item.name for item in properties if item.name],
                    **{k: v for k, v in template.dict().items() if k in ('name', 'description', 'eid')},
                }
                fs_handler.write(
                    fs_handler.join_path(base_path, 'templates', entity_type, f'metadata_{template.name}.json'),
                    json.dumps(metadata),
                )
        except TypeError:
            log.exception('There is no available templates for Task entity')
