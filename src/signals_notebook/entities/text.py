from typing import Literal

from pydantic import Field

from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.types import EntitySubtype, File


class Text(ContentfulEntity):
    type: Literal[EntitySubtype.TEXT] = Field(allow_mutation=False)

    @classmethod
    def _get_subtype(cls) -> EntitySubtype:
        return EntitySubtype.TEXT

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
