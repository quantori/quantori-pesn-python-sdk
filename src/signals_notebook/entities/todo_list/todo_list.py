import json
import logging
from json import JSONDecodeError
from typing import cast, ClassVar, Dict, List, Literal, Union
from uuid import UUID

from pydantic import Field, PrivateAttr

from signals_notebook.common_types import EID, EntityType, File
from signals_notebook.entities import EntityStore, Task
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.jinja_env import env
from signals_notebook.utils import FSHandler

log = logging.getLogger(__name__)


class TodoList(ContentfulEntity):
    type: Literal[EntityType.TODO_LIST] = Field(allow_mutation=False)
    _template_name: ClassVar = 'todo_list.html'
    _tasks: List[Task] = PrivateAttr(default=[])
    _tasks_by_id: Dict[EID, Task] = PrivateAttr(default={})

    def __getitem__(self, index: Union[int, str, UUID, EID]) -> Task:
        if not self._tasks:
            self._reload_tasks()

        if isinstance(index, int):
            return self._tasks[index]

        if isinstance(index, str):
            return self._tasks_by_id[EID(index)]

        if isinstance(index, EID):
            return self._tasks_by_id[index]

        raise IndexError('Invalid index')

    def __iter__(self):
        if not self._tasks:
            self._reload_tasks()
        return self._tasks.__iter__()

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.TODO_LIST

    def _reload_tasks(self) -> None:
        log.debug('Reloading tasks in TodoList: %s...', self.eid)
        self._tasks = []
        self._tasks_by_id = {}
        file = self.get_content()
        content = file.content.decode('utf-8')
        try:
            dict_content = json.loads(content)
        except JSONDecodeError:
            return
        for item in dict_content['rows']:
            row = EntityStore.get(item['eid'])
            task = cast(Task, row)
            assert task.eid

            self._tasks.append(task)
            self._tasks_by_id[task.eid] = task
        log.debug('Tasks in TodoList: %s were reloaded', self.eid)

    def save(self, force: bool = True) -> None:
        """Save all changes in the TodoList

        Args:
            force: Force to update properties without digest check.

        Returns:

        """

        log.debug('Saving TodoList: %s...', self.eid)
        for item in self._tasks:
            item.save(force=force)
        self._reload_tasks()
        log.debug('TodoList: %s was saved successfully', self.eid)

    def get_content(self) -> File:
        """Get TodoList content

        Returns:
            File
        """
        return super()._get_content()

    def get_html(self) -> str:
        """Get in HTML format

        Returns:
            Rendered template as a string
        """

        file = self.get_content()
        template = env.get_template(self._template_name)
        content = file.content.decode('utf-8')
        try:
            dict_content = json.loads(content)
        except json.JSONDecodeError:
            return template.render(name=self.name)

        table_head = dict_content['cols']
        rows = dict_content['rows']
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(name=self.name, table_head=table_head, rows=rows)

    def dump(self, base_path: str, fs_handler: FSHandler) -> None:  # type: ignore[override]
        """Dump TodoList entity

        Args:
            base_path: content path where create dump
            fs_handler: FSHandler

        Returns:

        """
        super().dump(base_path=base_path, fs_handler=fs_handler)
        for item in self:
            tasks_path = fs_handler.join_path(base_path, self.eid)
            item.dump(base_path=tasks_path, fs_handler=fs_handler)
