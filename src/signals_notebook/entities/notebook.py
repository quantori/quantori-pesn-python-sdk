from typing import Literal, Optional

from pydantic import BaseModel, Field

from signals_notebook.entities.container import Container
from signals_notebook.types import EntityCreationRequestPayload, EntityType


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

        request = _RequestPayload(
            data=_RequestBody(
                type=cls._get_entity_type(),
                attributes=_Attributes(
                    name=name,
                    description=description,
                ),
            )
        )

        return super()._create(
            digest=digest,
            force=force,
            request=request,
        )
