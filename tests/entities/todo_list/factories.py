import factory

from signals_notebook.common_types import EntityType, ObjectType
from signals_notebook.entities import Task, TaskCell, TaskContainer, TodoList
from tests.entities.factories import EntityFactory


class TodoListFactory(EntityFactory):
    class Meta:
        model = TodoList

    type = EntityType.TODO_LIST


class TaskFactory(EntityFactory):
    class Meta:
        model = Task

    type = EntityType.TASK


class TaskCellFactory(factory.Factory):
    id = factory.Faker('word')
    type = ObjectType.PROPERTY
    content = factory.Dict({'value': 4})

    class Meta:
        model = TaskCell


class TaskContainerFactory(EntityFactory):
    class Meta:
        model = TaskContainer

    type = EntityType.TASK_CONTAINER
