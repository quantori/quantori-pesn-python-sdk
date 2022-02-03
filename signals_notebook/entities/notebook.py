from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from signals_notebook.entities.entity import Entity
from signals_notebook.types import EntityCreationRequestPayload, EntitySubtype


class _Attributes(BaseModel):
    name: str
    description: Optional[str] = None


class _RequestBody(BaseModel):
    type: EntitySubtype
    attributes: _Attributes


class _RequestPayload(EntityCreationRequestPayload[_RequestBody]):
    pass


class Notebook(Entity):
    name: str = Field(title='Name')
    description: Optional[str] = Field(title='Description', default=None)
    created_at: datetime = Field(alias='createdAt', allow_mutation=False)
    edited_at: datetime = Field(alias='editedAt', allow_mutation=False)

    @classmethod
    def get_subtype(cls) -> EntitySubtype:
        return EntitySubtype.NOTEBOOK

    @classmethod
    def create(
        cls, *, name: str, description: Optional[str] = None, digest: str = None, force: bool = True
    ) -> 'Notebook':

        request = _RequestPayload(
            data=_RequestBody(
                type=cls.get_subtype(),
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
