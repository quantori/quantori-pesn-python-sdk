import logging
from enum import Enum
from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.jinja_env import env

log = logging.getLogger(__name__)


class Text(ContentfulEntity):
    class ContentType(str, Enum):
        TXT = 'text/plain'
        TXT_HTML = 'text/html'

    type: Literal[EntityType.TEXT] = Field(allow_mutation=False)
    _template_name: ClassVar = 'text.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.TEXT

    @classmethod
    def create(
        cls,
        *,
        container: Container,
        name: str,
        content_type: str = ContentType.TXT,
        content: bytes = b'',
        force: bool = True,
    ) -> Entity:
        """Create Text entity

        Args:
            container: Container where create new Text
            name: file name
            content_type: content type of Text entity
            content: Text content
            force: Force to post attachment

        Returns:
            Text
        """
        cls.ContentType(content_type)
        log.debug('Create entity: %s with name: %s in Container: %s', cls.__name__, name, container.eid)
        return container.add_child(
            name=name,
            content=content,
            content_type=cls.ContentType.TXT.value,
            force=force,
        )

    def get_content(self) -> File:
        """Get Text content

        Returns:
            File
        """
        return super()._get_content()

    def get_html(self) -> str:
        """Get in HTML format

        Returns:
            Rendered template as a string
        """
        file = self._get_content()
        data = {'name': self.name, 'content': file.content.decode('utf-8')}
        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(data=data)
