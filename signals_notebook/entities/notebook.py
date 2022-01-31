from datetime import datetime

from pydantic import Field

from signals_notebook.entities.entity import Entity
from signals_notebook.types import EntitySubtype


class Notebook(Entity):
    name: str
    description: str
    created_at: datetime = Field(alias='createdAt', allow_mutation=False)
    edited_at: datetime = Field(alias='editedAt', allow_mutation=False)
    digest: str = Field(allow_mutation=False)

    @classmethod
    def get_subtype(cls) -> EntitySubtype:
        return EntitySubtype.NOTEBOOK

    @classmethod
    def create(cls, *, name: str, description: str, **kwargs) -> 'Notebook':
        return super().create(attributes={'name': name, 'description': description}, **kwargs)
