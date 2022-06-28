import factory

from signals_notebook.common_types import EntityType
from signals_notebook.entities import Task, TaskProperty, TodoList
from tests.entities.factories import EntityFactory


class TodoListFactory(EntityFactory):
    class Meta:
        model = TodoList

    type = EntityType.TODO_LIST


class TaskFactory(EntityFactory):
    class Meta:
        model = Task

    type = EntityType.TASK


class TaskPropertyFactory(factory.Factory):
    id = factory.Faker('word')
    type = 'property'
    content = factory.Dict({'value': 4})

    class Meta:
        model = TaskProperty
