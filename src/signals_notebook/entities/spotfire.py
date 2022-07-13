import json
import logging
from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.utils.fs_handler import FSHandler

log = logging.getLogger(__name__)


class Spotfire(ContentfulEntity):
    type: Literal[EntityType.SPOTFIRE] = Field(allow_mutation=False)
    _template_name: ClassVar = 'spotfire.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.SPOTFIRE

    @classmethod
    def create(cls, *, container: Container, name: str, content: bytes = b'', force: bool = True) -> Entity:
        """Create Spotfiredxp Entity

        Args:
            container: Container where create new Excel
            name: file name
            content: Excel content
            force: Force to post attachment

        Returns:
            Spotfiredxp
        """
        log.debug('Create entity: %s with name: %s in Container: %s', cls.__name__, name, container.eid)
        return container.add_child(
            name=name,
            content=content,
            content_type='application/vnd.spotfire.dxp',
            force=force,
        )

    def get_content(self) -> File:
        """Get Spotfire content

        Returns:
            File
        """
        return super()._get_content()

    def dump(self, base_path: str, fs_handler: FSHandler):
        content = self.get_content()
        metadata = {'file_name': content.name, **self.dict()}
        fs_handler.write(fs_handler.join_path(base_path, self.eid, 'metadata.json'), json.dumps(metadata))
        file_name = content.name
        data = content.content
        fs_handler.write(fs_handler.join_path(base_path, self.eid, file_name), data)

    @classmethod
    def load(cls, path: str, fs_handler: FSHandler, parent: Container):
        metadata_path = fs_handler.join_path(path, 'metadata.json')
        metadata = json.loads(fs_handler.read(metadata_path))
        content_path = fs_handler.join_path(path, metadata['file_name'])
        content = fs_handler.read(content_path)
        cls.create(container=parent, name=metadata['name'], content=content, force=True)
