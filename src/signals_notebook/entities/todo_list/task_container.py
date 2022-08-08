from typing import Literal

from pydantic import Field

from signals_notebook.common_types import EntityType
from signals_notebook.entities import TodoList


class TaskContainer(TodoList):
    type: Literal[EntityType.TASK_CONTAINER] = Field(allow_mutation=False)
    _template_name: str = 'task_container.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.TASK_CONTAINER