from functools import cached_property
from typing import Literal, Optional, Union

from pydantic import Field

from signals_notebook.common_types import ChemicalDrawingFormat, EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.entities.stoichiometry.stoichiometry import Stoichiometry


class ChemicalDrawing(ContentfulEntity):
    type: Literal[EntityType.CHEMICAL_DRAWING] = Field(allow_mutation=False)

    class Config:
        keep_untouched = (cached_property,)

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

    @cached_property
    def stoichiometry(self) -> Union[Stoichiometry, list[Stoichiometry]]:
        return Stoichiometry.fetch_data(self.eid)
