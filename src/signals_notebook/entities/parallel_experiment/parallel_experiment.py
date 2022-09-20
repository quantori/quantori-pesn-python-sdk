import json
import logging
from enum import Enum
from functools import cached_property
from typing import Any, ClassVar, Generator, Literal, Optional

from pydantic import BaseModel, Field

from signals_notebook.common_types import (
    Ancestors,
    EntityCreationRequestPayload,
    EntityType,
    Template,
)
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.notebook import Notebook
from signals_notebook.jinja_env import env
from signals_notebook.utils.fs_handler import FSHandler

log = logging.getLogger(__name__)


class ParaExperimentState(str, Enum):
    OPEN = 'open'
    CLOSED = 'closed'


class _Attributes(BaseModel):
    name: str
    description: Optional[str] = None


class _Relationships(BaseModel):
    template: Optional[Template] = None
    ancestors: Optional[Ancestors] = None


class _RequestBody(BaseModel):
    type: EntityType
    attributes: _Attributes
    relationships: Optional[_Relationships] = None


class _RequestPayload(EntityCreationRequestPayload[_RequestBody]):
    pass


class ParallelExperiment(Container):
    type: Literal[EntityType.PARALLEL_EXPERIMENT] = Field(allow_mutation=False)
    state: Optional[ParaExperimentState] = Field(allow_mutation=False, default=None)
    _template_name: ClassVar = 'parallel_experiment.html'

    class Config:
        keep_untouched = (cached_property,)

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.PARALLEL_EXPERIMENT

    @classmethod
    def create(
        cls,
        *,
        name: str,
        description: Optional[str] = None,
        template: Optional['ParallelExperiment'] = None,
        notebook: Optional[Notebook] = None,
        digest: str = None,
        force: bool = True,
    ) -> 'ParallelExperiment':
        """Create new Parallel Experiment in Signals Notebook

        Args:
            name: name of parallel experiment
            description: description of parallel experiment
            template: parallel experiment template
            notebook: notebook where create parallel experiment
            digest: Indicate digest
            force: Force to create without doing digest check

        Returns:
            ParallelExperiment
        """

        relationships = None
        if template or notebook:
            relationships = _Relationships(
                ancestors=Ancestors(data=[notebook.short_description]) if notebook else None,
                template=Template(data=template.short_description) if template else None,
            )

        request = _RequestPayload(
            data=_RequestBody(
                type=cls._get_entity_type(),
                attributes=_Attributes(
                    name=name,
                    description=description,
                ),
                relationships=relationships,
            )
        )

        log.debug('Creating Parallel Experiment for: %s', cls.__name__)
        return super()._create(
            digest=digest,
            force=force,
            request=request,
        )

    def get_children(self, order='') -> Generator[Entity, None, None]:
        """Get children of SubExperiment.

        Returns:
            list of Entities
        """
        return super().get_children(order=order)

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

    @classmethod
    def load(cls, path: str, fs_handler: FSHandler, notebook: Notebook) -> None:
        cls._load(path, fs_handler, notebook)

    @classmethod
    def _load(cls, path: str, fs_handler: FSHandler, parent: Any) -> None:
        from signals_notebook.item_mapper import ItemMapper

        metadata = json.loads(fs_handler.read(fs_handler.join_path(path, 'metadata.json')))
        experiment = cls.create(
            notebook=parent, name=metadata['name'], description=metadata['description'], force=True
        )
        experiment_children = [
            child for child in experiment.get_children() if child.type != EntityType.SUB_EXPERIMENT_SUMMARY
        ]

        for child_entity in experiment_children:
            child_entity.delete()

        child_entities_folders = fs_handler.list_subfolders(path)
        for folder in child_entities_folders:
            child_entity_type = folder.split(':')[0]
            try:
                ItemMapper.get_item_class(child_entity_type)._load(
                    fs_handler.join_path(path, folder), fs_handler, experiment
                )
            except NotImplementedError:
                log.info('Entity %s is not implemented.', folder)
