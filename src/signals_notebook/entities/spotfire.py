import logging
from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity

log = logging.getLogger(__name__)


class Spotfire(ContentfulEntity):
    type: Literal[EntityType.SPOTFIRE] = Field(allow_mutation=False)
    _template_name: ClassVar = 'spotfire.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.SPOTFIRE

    @classmethod
    def create(cls, *, container: Container, name: str, content: bytes = b'', force: bool = True) -> Entity:
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
