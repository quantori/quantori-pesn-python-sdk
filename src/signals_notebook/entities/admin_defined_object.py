import logging
from functools import cached_property
from typing import ClassVar, Literal, Optional

from pydantic import Field

from signals_notebook.common_types import EntityType
from signals_notebook.entities import Notebook
from signals_notebook.entities.container import Container
from signals_notebook.jinja_env import env
from signals_notebook.utils import FSHandler

log = logging.getLogger(__name__)


class AdminDefinedObject(Container):
    type: Literal[EntityType.ADO] = Field(allow_mutation=False)
    _template_name: ClassVar = 'ado.html'

    class Config:
        keep_untouched = (cached_property,)

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.ADO

    # @classmethod
    # def create(
    #     cls,
    #     *,
    #     name: str,
    #     description: Optional[str] = None,
    #     template: Optional['AdminDefinedObject'] = None,
    #     notebook: Optional[Notebook] = None,
    #     digest: str = None,
    #     force: bool = True,
    # ) -> 'AdminDefinedObject':
    #     """Create new AdminDefinedObject in Signals Notebook
    #
    #     Args:
    #         name: name of experiment
    #         description: description of experiment
    #         template: experiment template
    #         notebook: notebook where create experiment
    #         digest: Indicate digest
    #         force: Force to create without doing digest check
    #
    #     Returns:
    #         AdminDefinedObject
    #     """
    #
    #     relationships = None
    #     if template or notebook:
    #         relationships = _Relationships(
    #             ancestors=Ancestors(data=[notebook.short_description]) if notebook else None,
    #             template=Template(data=template.short_description) if template else None,
    #         )
    #
    #     request = _RequestPayload(
    #         data=_RequestBody(
    #             type=cls._get_entity_type(),
    #             attributes=_Attributes(
    #                 name=name,
    #                 description=description,
    #             ),
    #             relationships=relationships,
    #         )
    #     )
    #
    #     log.debug('Creating Notebook for: %s', cls.__name__)
    #     return super()._create(
    #         digest=digest,
    #         force=force,
    #         request=request,
    #     )

    def get_html(self) -> str:
        """Get in HTML format

        Returns:
            Rendered template as a string
        """
        data = {
            'title': self.name,
            'description': self.description,
            'edited_at': self.edited_at,
            'children': self.get_children()
        }

        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(data=data)

    # @classmethod
    # def load(cls, path: str, fs_handler: FSHandler, notebook: Notebook) -> None:
    #     from signals_notebook.item_mapper import ItemMapper
    #
    #     metadata = json.loads(fs_handler.read(fs_handler.join_path(path, 'metadata.json')))
    #     experiment = cls.create(
    #         notebook=notebook, name=metadata['name'], description=metadata['description'], force=True
    #     )
    #     child_entities_folders = fs_handler.list_subfolders(path)
    #     for child_entity in child_entities_folders:
    #         child_entity_type = child_entity.split(':')[0]
    #         ItemMapper.get_item_class(child_entity_type).load(
    #             fs_handler.join_path(path, child_entity), fs_handler, experiment
    #         )
