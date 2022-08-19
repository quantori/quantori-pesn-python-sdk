import logging
from typing import Generator, Literal, Optional

from pydantic import BaseModel, Field

from signals_notebook.entities import Entity
from signals_notebook.common_types import EntityCreationRequestPayload, EntityType
from signals_notebook.entities.container import Container

log = logging.getLogger(__name__)


class _Attributes(BaseModel):
    name: str
    description: Optional[str] = None


class _RequestBody(BaseModel):
    type: EntityType
    attributes: _Attributes


class _RequestPayload(EntityCreationRequestPayload[_RequestBody]):
    pass


class Notebook(Container):
    type: Literal[EntityType.NOTEBOOK] = Field(allow_mutation=False)

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.NOTEBOOK

    @classmethod
    def create(
        cls,
        *,
        name: str,
        description: Optional[str] = None,
        digest: str = None,
        force: bool = True,
    ) -> 'Notebook':
        """Create Notebook in Signals Notebooks

        Args:
            name: Notebook name
            description: Notebook description
            digest: Indicate digest
            force: Force to create without doing digest check

        Returns:

        """

        request = _RequestPayload(
            data=_RequestBody(
                type=cls._get_entity_type(),
                attributes=_Attributes(
                    name=name,
                    description=description,
                ),
            )
        )

        log.debug('Creating Notebook for: %s', cls.__name__)
        return super()._create(
            digest=digest,
            force=force,
            request=request,
        )

    def get_children(self, order: str = 'layout') -> Generator[Entity, None, None]:
        """Get children of Notebook.

        Returns:
            list of Entities
        """
        return super().get_children(order='')
