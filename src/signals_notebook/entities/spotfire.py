import logging
from enum import Enum
from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity

log = logging.getLogger(__name__)


class Spotfire(ContentfulEntity):
    class ContentType(str, Enum):
        DXP = 'application/vnd.spotfire.dxp'

    type: Literal[EntityType.SPOTFIRE] = Field(allow_mutation=False)
    _template_name: ClassVar = 'spotfire.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.SPOTFIRE

    @classmethod
    def create(
        cls,
        *,
        container: Container,
        name: str,
        content_type: str = ContentType.DXP,
        content: bytes = b'',
        force: bool = True,
    ) -> Entity:
        """Create Spotfiredxp Entity

        Args:
            container: Container where create new Excel
            name: file name
            content_type: content type of Spotfire entity
            content: Excel content
            force: Force to post attachment

        Returns:
            Spotfiredxp
        """
        cls.ContentType(content_type)
        log.debug('Create entity: %s with name: %s in Container: %s', cls.__name__, name, container.eid)
        return container.add_child(
            name=name,
            content=content,
            content_type=content_type,
            force=force,
        )

    def get_content(self) -> File:
        """Get Spotfire content

        Returns:
            File
        """
        return super()._get_content()
