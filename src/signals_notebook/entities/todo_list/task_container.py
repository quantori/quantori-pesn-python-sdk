from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType
from signals_notebook.entities import TodoList


class TaskContainer(TodoList):
    type: Literal[EntityType.TASK_CONTAINER] = Field(allow_mutation=False)  # type: ignore
    _template_name: ClassVar = 'task_container.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.TASK_CONTAINER
