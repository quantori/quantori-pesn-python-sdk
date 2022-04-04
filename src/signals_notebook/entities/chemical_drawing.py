from enum import Enum
from typing import Literal, Optional

from pydantic import Field

from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.common_types import EntityType, File


class ChemicalDrawingFormat(str, Enum):
    CDXML = 'cdxml'
    SVG = 'svg'
    MOL = 'mol'
    MOL3000 = 'mol-v3000'
    SMILES = 'smiles'


class ChemicalDrawing(ContentfulEntity):
    type: Literal[EntityType.CHEMICAL_DRAWING] = Field(allow_mutation=False)

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.CHEMICAL_DRAWING

    @classmethod
    def create(
        cls,
        *,
        container: Container,
        name: str,
        content_type: str,
        content: bytes = b'',
        force: bool = True,
    ) -> Entity:
        return container.add_child(
            name=name,
            content=content,
            content_type=content_type,
            force=force,
        )

    def get_content(self, format: Optional[ChemicalDrawingFormat] = None) -> File:
        return super()._get_content(format=format)
