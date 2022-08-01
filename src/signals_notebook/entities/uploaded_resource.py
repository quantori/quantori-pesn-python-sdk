import logging
from enum import Enum
from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity

log = logging.getLogger(__name__)


class UploadedResource(ContentfulEntity):
    class ContentType(str, Enum):
        BINARY = 'application/octet-stream'

    type: Literal[EntityType.UPLOADED_RESOURCE] = Field(allow_mutation=False)
    _template_name: ClassVar = 'uploaded_resource.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.UPLOADED_RESOURCE

    @classmethod
    def create(
        cls,
        *,
        container: Container,
        name: str,
        content: bytes = b'',
        content_type: str = ContentType.BINARY,
        force: bool = True,
    ) -> Entity:
        """Create UploadedResource Entity

        Args:
            container: Container where create new UploadedResource
            name: file name
            content: UploadedResource content
            content_type: UploadedResource content type
            force: Force to post attachment

        Returns:
            UploadedResource
        """
        log.debug('Create entity: %s with name: %s in Container: %s', cls.__name__, name, container.eid)
        return container.add_child(
            name=name,
            content=content,
            content_type=content_type,
            force=force,
        )

    def get_content(self) -> File:
        """Get UploadedResource content

        Returns:
            File
        """
        return super()._get_content()
