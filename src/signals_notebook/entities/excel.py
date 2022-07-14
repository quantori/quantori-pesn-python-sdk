import json
import logging
from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.utils import FSHandler

log = logging.getLogger(__name__)


class Excel(ContentfulEntity):
    type: Literal[EntityType.EXCEL] = Field(allow_mutation=False)
    _template_name: ClassVar = 'excel.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.EXCEL

    @classmethod
    def create(cls, *, container: Container, name: str, content: bytes = b'', force: bool = True) -> Entity:
        """Create Excel Entity

        Args:
            container: Container where create new Excel
            name: file name
            content: Excel content
            force: Force to post attachment

        Returns:
            Excel
        """
        log.debug('Create entity: %s with name: %s in Container: %s', cls.__name__, name, container.eid)
        return container.add_child(
            name=name,
            content=content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            force=force,
        )

    def get_content(self) -> File:
        """Get Excel content

        Returns:
            File
        """
        return super()._get_content()

    def dump(self, base_path: str, fs_handler: FSHandler) -> None:
        """Dump Excel entity

        Args:
            base_path: content path where create dump
            fs_handler: FSHandler

        Returns:

        """
        content = self.get_content()
        metadata = {
            'file_name': content.name,
            **{k: v for k, v in self.dict().items() if k in ('name', 'description', 'eid')},
        }
        fs_handler.write(fs_handler.join_path(base_path, self.eid, 'metadata.json'), json.dumps(metadata))
        file_name = content.name
        data = content.content
        fs_handler.write(fs_handler.join_path(base_path, self.eid, file_name), data)

    @classmethod
    def load(cls, path: str, fs_handler: FSHandler, parent: Container) -> None:
        """Load Excel entity

        Args:
            path: content path
            fs_handler: FSHandler
            parent: Container where load Excel entity

        Returns:

        """
        metadata_path = fs_handler.join_path(path, 'metadata.json')
        metadata = json.loads(fs_handler.read(metadata_path))
        content_path = fs_handler.join_path(path, metadata['file_name'])
        content = fs_handler.read(content_path)
        cls.create(container=parent, name=metadata['name'], content=content, force=True)
