import logging
from enum import Enum
from functools import cached_property
from typing import ClassVar, Literal, Optional, Union

from pydantic import Field

from signals_notebook.common_types import EntityType
from signals_notebook.entities.container import Container
from signals_notebook.entities.stoichiometry.stoichiometry import Stoichiometry
from signals_notebook.jinja_env import env

log = logging.getLogger(__name__)


class ParaExperimentState(str, Enum):
    OPEN = 'open'
    CLOSED = 'closed'


class ParallelExperiment(Container):
    type: Literal[EntityType.PARALLEL_EXPERIMENT] = Field(allow_mutation=False)
    state: Optional[ParaExperimentState] = Field(allow_mutation=False, default=None)
    _template_name: ClassVar = 'para_experiment.html'

    class Config:
        keep_untouched = (cached_property,)

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.PARALLEL_EXPERIMENT

    # @classmethod
    # def create(
    #         cls,
    #         *,
    #         name: str,
    #         description: Optional[str] = None,
    #         template: Optional['Experiment'] = None,
    #         notebook: Optional[Notebook] = None,
    #         digest: str = None,
    #         force: bool = True,
    # ) -> 'Notebook':
    #     """Create new Parallel Experiment in Signals Notebook
    #
    #     Args:
    #         name: name of parallel experiment
    #         description: description of parallel experiment
    #         template: parallel experiment template
    #         notebook: notebook where create parallel experiment
    #         digest: Indicate digest
    #         force: Force to create without doing digest check
    #
    #     Returns:
    #         ParallelExperiment
    #     """
    #
    #     relationships = None
    #     if template or notebook:
    #         relationships = _Relationships(
    #             ancestors=Ancestors(data=[notebook.short_description]) if notebook else None,
    #             template=Template(data=template.short_description) if template else None,
    #         )
    #
    #     request = _RequestPayload(
    #         data=_RequestBody(
    #             type=cls._get_entity_type(),
    #             attributes=_Attributes(
    #                 name=name,
    #                 description=description,
    #             ),
    #             relationships=relationships,
    #         )
    #     )
    #
    #     log.debug('Creating Notebook for: %s', cls.__name__)
    #     return super()._create(
    #         digest=digest,
    #         force=force,
    #         request=request,
    #     )

    @cached_property
    def stoichiometry(self) -> Union[Stoichiometry, list[Stoichiometry]]:
        """ Fetch stoichiometry data of parallel experiment

        Returns:
            Stoichiometry object or list of Stoichiometry objects
        """
        log.debug('Fetching data in Stoichiometry for: %s', self.eid)
        return Stoichiometry.fetch_data(self.eid)

    def get_html(self) -> str:
        """Get in HTML format

        Returns:
            Rendered template as a string
        """
        data = {
            'title': self.name,
            'description': self.description,
            'edited_at': self.edited_at,
            'state': self.state,
            'children': self.get_children(),
        }

        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(data=data)
