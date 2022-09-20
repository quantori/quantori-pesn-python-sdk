import logging
from enum import Enum
from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity

log = logging.getLogger(__name__)


class PowerPoint(ContentfulEntity):
    class ContentType(str, Enum):
        PPTX = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        PPSX = 'application/vnd.openxmlformats-officedocument.presentationml.slideshow'
        POTX = 'application/vnd.openxmlformats-officedocument.presentationml.template'
        PPTM = 'application/vnd.ms-powerpoint.presentation.macroEnabled.12'
        PPSM = 'application/vnd.ms-powerpoint.slideshow.macroEnabled.12'
        POTM = 'application/vnd.ms-powerpoint.presentation.macroEnabled.12'
        PPT = 'application/vnd.ms-powerpoint'

    type: Literal[EntityType.POWER_POINT] = Field(allow_mutation=False)
    _template_name: ClassVar = 'power_point.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.POWER_POINT

    @classmethod
    def create(
        cls,
        *,
        container: Container,
        name: str,
        content_type: str = ContentType.PPTX,
        content: bytes = b'',
        force: bool = True,
    ) -> Entity:
        """Create PowerPoint Entity

        Args:
            container: Container where create new PowerPoint
            name: file name
            content_type: content type of PowerPoint entity
            content: PowerPoint content
            force: Force to post attachment

        Returns:
            PowerPoint
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
        """Get PowerPoint content

        Returns:
            File
        """
        return super()._get_content()
