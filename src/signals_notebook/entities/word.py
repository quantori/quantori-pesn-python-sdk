from typing import Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity


class Word(ContentfulEntity):
    type: Literal[EntityType.WORD] = Field(allow_mutation=False)

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.WORD

    @classmethod
    def create(cls, *, container: Container, name: str, content: str = '', force: bool = True) -> Entity:
        return container.add_child(
            name=name,
            content=content.encode('utf-8'),
            content_type='text/plain',
            force=force,
        )

    def get_content(self) -> File:
        return super()._get_content()
