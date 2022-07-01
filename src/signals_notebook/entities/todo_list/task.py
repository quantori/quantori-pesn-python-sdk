import json
import logging
from typing import cast, Dict, List, Literal, Union
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
