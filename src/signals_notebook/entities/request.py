import json
import logging
from functools import cached_property
from typing import Literal, ClassVar, Optional

from pydantic import Field

from signals_notebook.common_types import EntityType
from signals_notebook.entities import Notebook
from signals_notebook.entities.container import Container
from signals_notebook.jinja_env import env
from signals_notebook.utils import FSHandler

log = logging.getLogger(__name__)


class Request(Container):
    type: Literal[EntityType.REQUEST] = Field(allow_mutation=False)
    _template_name: ClassVar = 'request.html'

    class Config:
        keep_untouched = (cached_property,)

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.REQUEST

    @classmethod
    def create(
        cls,
        *,
        name: str,
        description: Optional[str] = None,
        template: Optional['Request'] = None,
        notebook: Optional[Notebook] = None,
        digest: str = None,
        force: bool = True,
    ) -> 'Request':
        raise NotImplementedError

    def get_html(self) -> str:
        """Get in HTML format

        Returns:
            Rendered template as a string
        """
        data = {
            'title': self.name,
            'description': self.description,
            'edited_at': self.edited_at,
            'children': self.get_children(),
        }

        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(data=data)

    @classmethod
    def load(cls, path: str, fs_handler: FSHandler, notebook: Notebook) -> None:
        from signals_notebook.item_mapper import ItemMapper

        metadata = json.loads(fs_handler.read(fs_handler.join_path(path, 'metadata.json')))
        experiment = cls.create(
            notebook=notebook, name=metadata['name'], description=metadata['description'], force=True
        )
        child_entities_folders = fs_handler.list_subfolders(path)
        for child_entity in child_entities_folders:
            child_entity_type = child_entity.split(':')[0]
            ItemMapper.get_item_class(child_entity_type).load(
                fs_handler.join_path(path, child_entity), fs_handler, experiment
            )
