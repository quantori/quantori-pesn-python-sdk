import logging
from functools import cached_property
from typing import Generator, Literal, Optional

from pydantic import BaseModel, Field

from signals_notebook.common_types import (
    Ancestors,
    EntityCreationRequestPayload,
    EntityType,
    Template,
)
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.parallel_experiment.parallel_experiment import ParallelExperiment
from signals_notebook.jinja_env import env

log = logging.getLogger(__name__)


class _SubExperimentAttributes(BaseModel):
    description: Optional[str] = None


class _SubExperimentRelationships(BaseModel):
    template: Optional[Template] = None
    ancestors: Optional[Ancestors] = None


class _SubExperimentRequestBody(BaseModel):
    type: EntityType
    attributes: Optional[_SubExperimentAttributes]
    relationships: Optional[_SubExperimentRelationships] = None


class _SubExperimentRequestPayload(EntityCreationRequestPayload[_SubExperimentRequestBody]):
    pass


class SubExperiment(Container):
    type: Literal[EntityType.SUB_EXPERIMENT] = Field(allow_mutation=False)
    _template_name = 'sub_experiment.html'

    class Config:
        keep_untouched = (cached_property,)

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.SUB_EXPERIMENT

    def get_children(self, order='') -> Generator[Entity, None, None]:
        """Get children of SubExperiment.

        Returns:
            list of Entities
        """
        return super().get_children(order=order)

    @classmethod
    def create(
        cls,
        *,
        parallel_experiment: ParallelExperiment,
        description: Optional[str] = None,
        template: Optional['SubExperiment'] = None,
        digest: str = None,
        force: bool = True,
    ) -> 'SubExperiment':

        relationships = None
        if template or parallel_experiment:
            relationships = _SubExperimentRelationships(
                ancestors=Ancestors(data=[parallel_experiment.short_description]) if parallel_experiment else None,
                template=Template(data=template.short_description) if template else None,
            )

        request = _SubExperimentRequestPayload(
            data=_SubExperimentRequestBody(
                type=cls._get_entity_type(),
                attributes=_SubExperimentAttributes(description=description),
                relationships=relationships,
            )
        )

        return super()._create(
            digest=digest,
            force=force,
            request=request,
        )

    def get_html(self) -> str:
        """Get in HTML format

        Returns:
            Rendered template as a string
        """
        data = {
            'title': self.name,
            'description': self.description,
            'edited_at': self.edited_at,
            'children': self.get_children(),
        }

        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(data=data)
