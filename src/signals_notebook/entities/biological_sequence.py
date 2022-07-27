import logging
import mimetypes
from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.jinja_env import env

log = logging.getLogger(__name__)


class BiologicalSequence(ContentfulEntity):
    type: Literal[EntityType.BIO_SEQUENCE] = Field(allow_mutation=False)
    _template_name: ClassVar = 'bio_sequence.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.BIO_SEQUENCE

    @classmethod
    def create(
        cls,
        *,
        container: Container,
        name: str,
        content: bytes = b'',
        file_extension: str = '',
        force: bool = True,
    ) -> Entity:
        """Create BiologicalSequence Entity

        Args:
            container: Container where create new BiologicalSequence
            name: file name
            content: BiologicalSequence content
            file_extension: BiologicalSequence extension
            force: Force to post attachment

        Returns:
            BiologicalSequence
        """
        log.debug('Create entity: %s with name: %s in Container: %s', cls.__name__, name, container.eid)

        file_extension = file_extension.replace('.', '')
        content_type = mimetypes.types_map.get(f'.{file_extension}', 'biosequence/genbank')
        return container.add_child(
            name=name,
            content=content,
            content_type=content_type,
            force=force,
        )

    def get_content(self) -> File:
        return super()._get_content()

    def get_html(self) -> str:
        """Get in HTML format

        Returns:
            Rendered template as a string
        """
        data = {'name': self.name}
        file = self.get_content()
        data['bio_sequence'] = 'data:{};base64,{}'.format(file.content_type, file.base64.decode('ascii'))

        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(data=data)
