import logging
from enum import Enum
from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity

log = logging.getLogger(__name__)


class Word(ContentfulEntity):
    class ContentType(str, Enum):
        DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        DOTX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.template'
        DOCM = 'application/vnd.ms-word.document.macroEnabled.12'
        DOTM = 'application/vnd.ms-word.template.macroEnabled.12'
        DOC = 'application/msword'

    type: Literal[EntityType.WORD] = Field(allow_mutation=False)
    _template_name: ClassVar = 'word.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.WORD

    @classmethod
    def create(
        cls,
        *,
        container: Container,
        name: str,
        content_type: str = ContentType.DOCX,
        content: bytes = b'',
        force: bool = True,
    ) -> Entity:
        """Create Word Entity

        Args:
            container: Container where create new Word
            name: file name
            content_type: content type of Word entity
            content: Word content
            force: Force to post attachment

        Returns:

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
        """Get Word content

        Returns:
            File
        """
        return super()._get_content()
