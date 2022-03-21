import base64 as b64
import mimetypes
from typing import Literal

from pydantic import Field

from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.types import EntityType, File


class Image(ContentfulEntity):
    type: Literal[EntityType.IMAGE_RESOURCE] = Field(allow_mutation=False)

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.IMAGE_RESOURCE

    @classmethod
    def create(
        cls, *, container: Container, name: str, content: bytes = b'', file_extension: str = '', force: bool = True
    ) -> Entity:
        file_extension = file_extension.replace('.', '')
        content_type = mimetypes.types_map.get(f'.{file_extension}', 'application/octet-stream')
        return container.add_child(
            name=name,
            content=content,
            content_type=content_type,
            force=force,
        )

    def get_content(self, base64: bool = False) -> File:
        file = super()._get_content()
        if base64:
            file.content = b64.b64encode(file.content)

        return file
