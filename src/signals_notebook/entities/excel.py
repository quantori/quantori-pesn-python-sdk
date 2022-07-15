import logging
from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity

log = logging.getLogger(__name__)


class Excel(ContentfulEntity):
    type: Literal[EntityType.EXCEL] = Field(allow_mutation=False)
    _template_name: ClassVar = 'excel.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.EXCEL

    @classmethod
    def create(
        cls,
        *,
        container: Container,
        name: str,
        content_type: str = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        content: bytes = b'',
        force: bool = True,
    ) -> Entity:
        """Create Excel Entity

        Args:
            container: Container where create new Excel
            name: file name
            content_type: content type of Excel entity
            content: Excel content
            force: Force to post attachment

        Returns:
            Excel
        """
        log.debug('Create entity: %s with name: %s in Container: %s', cls.__name__, name, container.eid)
        return container.add_child(
            name=name,
            content=content,
            content_type=content_type,
            force=force,
        )

    def get_content(self) -> File:
        """Get Excel content

        Returns:
            File
        """
        return super()._get_content()
