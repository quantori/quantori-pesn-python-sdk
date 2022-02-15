from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field

from signals_notebook.entities.container import Container
from signals_notebook.entities.notebook import Notebook
from signals_notebook.types import Ancestors, EntityCreationRequestPayload, EntitySubtype, Template


class _Attributes(BaseModel):
    name: str
    description: Optional[str] = None


class _Relationships(BaseModel):
    template: Optional[Template] = None
    ancestors: Optional[Ancestors] = None


class _RequestBody(BaseModel):
    type: EntitySubtype
    attributes: _Attributes
    relationships: _Relationships


class _RequestPayload(EntityCreationRequestPayload[_RequestBody]):
    pass


class ExperimentState(str, Enum):
    OPEN = 'open'
    CLOSED = 'closed'


class Experiment(Container):
    type: Literal[EntitySubtype.EXPERIMENT] = Field(allow_mutation=False)
    state: Optional[ExperimentState] = None

    @classmethod
    def _get_subtype(cls) -> EntitySubtype:
        return EntitySubtype.EXPERIMENT

    def get_content(self, format: Optional[str] = None):
        raise NotImplementedError

    @classmethod
    def create(
        cls,
        *,
        name: str,
        description: Optional[str] = None,
        template: Optional['Experiment'] = None,
        notebook: Optional[Notebook] = None,
        digest: str = None,
        force: bool = True
    ) -> 'Notebook':

        relationships = None
        if template or notebook:
            relationships = _Relationships(
                ancestors=Ancestors(
                    data=[notebook.short_description]
                ) if notebook else None,
                template=Template(
                    data=template.short_description
                ) if template else None,
            )

        request = _RequestPayload(
            data=_RequestBody(
                type=cls._get_subtype(),
                attributes=_Attributes(
                    name=name,
                    description=description,
                ),
                relationships=relationships,
            )
        )

        return super()._create(
            digest=digest,
            force=force,
            request=request,
        )
