import json
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
from signals_notebook.entities.todo_list.cell import TaskProperty


class TaskPropertiesResponse(Response[TaskProperty]):
    pass


class Task(Entity):
    type: Literal[EntityType.TASK] = Field(allow_mutation=False)
    _properties: List[TaskProperty] = PrivateAttr(default=[])
    _properties_by_id: Dict[Union[str, UUID], TaskProperty] = PrivateAttr(default={})

    def __getitem__(self, index: Union[int, str, UUID]) -> TaskProperty:
        if not self._properties:
            self._reload_properties()

        if isinstance(index, int):
            return self._properties[index]

        if isinstance(index, str):
            try:
                return self._properties_by_id[UUID(index)]
            except ValueError:
                return self._properties_by_id[index]

        if isinstance(index, UUID):
            return self._properties_by_id[index]

        raise IndexError('Invalid index')

    def __iter__(self):
        if not self._properties:
            self._reload_properties()
        return self._properties.__iter__()

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.TASK

    @classmethod
    def _get_tasks_endpoint(cls) -> str:
        return 'tasks'

    def _reload_properties(self) -> None:
        self._properties = []
        self._properties_by_id = {}

        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_tasks_endpoint(), self.eid, 'properties'),
            params={'value': 'normalized'},
        )

        result = TaskPropertiesResponse(**response.json())
        properties = [cast(ResponseData, item).body for item in result.data]

        for item in properties:
            task_property = cast(TaskProperty, item)
            assert task_property.id

            self._properties.append(task_property)
            self._properties_by_id[task_property.id] = task_property

    def save(self, force: bool = True) -> None:
        api = SignalsNotebookApi.get_default_api()

        request_body = []
        for item in self._properties:
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
        self._reload_properties()
