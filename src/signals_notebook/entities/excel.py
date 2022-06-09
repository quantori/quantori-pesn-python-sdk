from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity


class Excel(ContentfulEntity):
    type: Literal[EntityType.EXCEL] = Field(allow_mutation=False)
    _template_name: ClassVar = 'excel.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.EXCEL

    @classmethod
    def create(cls, *, container: Container, name: str, content: str = '', force: bool = True) -> Entity:
        """Create Excel Entity

        Args:
            container: Container where create new Excel
            name: file name
            content: Excel content
            force: Force to post attachment

        Returns:
            Excel
        """
        return container.add_child(
            name=name,
            content=content.encode('utf-8'),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            force=force,
        )

    def get_content(self) -> File:
        """Get Excel content

        Returns:
            File
        """
        return super()._get_content()
