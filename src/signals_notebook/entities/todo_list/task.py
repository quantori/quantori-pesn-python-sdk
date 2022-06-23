import json
from typing import cast, Dict, List, Literal, Optional, TYPE_CHECKING, Union
from uuid import UUID

from pydantic import BaseModel, Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import (
    Ancestors,
    EntityCreationRequestPayload,
    EntityShortDescription,
    EntityType,
    Response,
    ResponseData,
)
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.todo_list.cell import TaskProperty

if TYPE_CHECKING:
    from signals_notebook.entities.todo_list.todo_list import TodoList


class _TaskAttributes(BaseModel):
    fields: Optional[List[TaskProperty]] = []


class _TaskRelationships(BaseModel):
    template: Optional[Dict[str, EntityShortDescription]] = None
    ancestors: Optional[Ancestors] = None


class _TaskRequestBody(BaseModel):
    type: EntityType
    attributes: _TaskAttributes
    relationships: Optional[_TaskRelationships] = None


class _TaskRequestPayload(EntityCreationRequestPayload[_TaskRequestBody]):
    pass


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

    @classmethod
    def create(
        cls,
        *,
        properties: Optional[List[TaskProperty]] = None,
        template: Optional['Task'] = None,
        ancestors: Optional[List[Union[Container, 'TodoList']]] = None,
        digest: str = None,
        force: bool = True,
    ) -> 'Task':
        relationships = None
        if template or ancestors:
            relationships = _TaskRelationships(
                ancestors=Ancestors(data=[item.short_description for item in ancestors]) if ancestors else None,
                template={'data': template.short_description} if template else None,
            )

        request = _TaskRequestPayload(
            data=_TaskRequestBody(
                type=cls._get_entity_type(),
                attributes=_TaskAttributes(fields=properties),
                relationships=relationships,
            )
        )

        return super()._create(
            digest=digest,
            force=force,
            request=request,
        )
