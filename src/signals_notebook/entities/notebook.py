from typing import Optional

from pydantic import BaseModel

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

    @classmethod
    def _get_subtype(cls) -> EntitySubtype:
        return EntitySubtype.NOTEBOOK

    def get_content(self, format: Optional[str] = None):
        raise NotImplementedError

    @classmethod
    def create(
        cls, *, name: str, description: Optional[str] = None, digest: str = None, force: bool = True
    ) -> 'Notebook':

        request = _RequestPayload(
            data=_RequestBody(
                type=cls._get_subtype(),
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
