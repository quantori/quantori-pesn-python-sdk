import logging
from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities.contentful_entity import ContentfulEntity

log = logging.getLogger(__name__)


class MaterialsTable(ContentfulEntity):
    type: Literal[EntityType.MATERIAL_TABLE] = Field(allow_mutation=False)
    _template_name: ClassVar = 'materials_table.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.MATERIAL_TABLE

    def get_content(self) -> File:
        return super()._get_content()
