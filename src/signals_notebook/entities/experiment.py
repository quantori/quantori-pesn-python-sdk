import json
import logging
from enum import Enum
from functools import cached_property
from typing import ClassVar, Generator, Literal, Optional, Union, Tuple

from pydantic import BaseModel, Field

from signals_notebook.common_types import Ancestors, EntityCreationRequestPayload, EntityType, Template
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.notebook import Notebook
from signals_notebook.entities.stoichiometry.stoichiometry import Stoichiometry
from signals_notebook.jinja_env import env
from signals_notebook.utils.fs_handler import FSHandler

log = logging.getLogger(__name__)


class _Attributes(BaseModel):
    name: str
    description: Optional[str] = None
    organization: Optional[str] = None
    department: Optional[str] = None
    project: Optional[str] = None
    modality: Optional[str] = None


class _Relationships(BaseModel):
    template: Optional[Template] = None
    ancestors: Optional[Ancestors] = None


class _RequestBody(BaseModel):
    type: EntityType
    attributes: _Attributes
    relationships: Optional[_Relationships] = None


class _RequestPayload(EntityCreationRequestPayload[_RequestBody]):
    pass


class ExperimentState(str, Enum):
    OPEN = 'open'
    CLOSED = 'closed'


class Experiment(Container):
    type: Literal[EntityType.EXPERIMENT] = Field(allow_mutation=False)
    state: Optional[ExperimentState] = Field(allow_mutation=False, default=None)
    _template_name: ClassVar = 'experiment.html'

    class Config:
        keep_untouched = (cached_property,)

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.EXPERIMENT

    @classmethod
    def create(
        cls,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        template: Optional['Experiment'] = None,
        notebook: Optional[Notebook] = None,
        digest: str = None,
        force: bool = True,
        attributes: dict = None
    ) -> 'Experiment':
        """Create new Experiment in Signals Notebook

        Args:
            name: name of experiment
            description: description of experiment
            template: experiment template
            notebook: notebook where create experiment
            digest: Indicate digest
            force: Force to create without doing digest check
            attributes:

        Returns:
            Experiment
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
                    **attributes
                ),
                relationships=relationships,
            )
        )

        log.debug('Creating Notebook for: %s', cls.__name__)
        return super()._create(
            digest=digest,
            force=force,
            request=request,
        )

    @cached_property
    def stoichiometry(self) -> Union[Stoichiometry, list[Stoichiometry]]:
        """Fetch stoichiometry data of experiment

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

    def get_children(self, order: Optional[str] = 'layout') -> Generator[Entity, None, None]:
        """Get children of Experiment.

        Returns:
            list of Entities
        """
        return super().get_children(order=order)

    @classmethod
    def load(cls, path: str, fs_handler: FSHandler, notebook: Notebook) -> None:  # type: ignore[override]
        """Load Experiment entity

        Args:
            path: content path
            fs_handler: FSHandler
            notebook: Container where load Experiment entity

        Returns:

        """
        from signals_notebook.item_mapper import ItemMapper

        metadata = json.loads(fs_handler.read(fs_handler.join_path(path, 'metadata.json')))
        try:
            experiment = cls.create(
                notebook=notebook, name=metadata['name'], description=metadata['description'],
                force=True,
                attributes=dict(
                    organization=metadata['Organization'],
                    project=metadata['Project'],
                    modality=metadata['Modality'],
                    department=metadata['Department']
                )
            )
        except Exception as e:
            log.error(str(e))
            if 'According to template, name is auto generated, can not be specified' in str(e):
                log.error('Retrying create')
                experiment = cls.create(
                    notebook=notebook, description=metadata['description'], force=True)
            else:
                raise e
        child_entities_folders = fs_handler.list_subfolders(path)
        for child_entity in child_entities_folders:
            child_entity_type = child_entity.split(':')[0]
            ItemMapper.get_item_class(child_entity_type).load(
                fs_handler.join_path(path, child_entity), fs_handler, experiment
            )

    def dump(self, base_path: str, fs_handler: FSHandler, alias: Optional[Tuple[str]] = None) -> None:
        metadata = {k: v for k, v in self.dict().items() if k in ('name', 'description', 'eid')}
        for property in self._properties:
            if property.name in ('Department', 'Project', 'Modality', 'Organization'):
                metadata[property.name] = property.value

        fs_handler.write(
            fs_handler.join_path(base_path, self.eid, 'metadata.json'),
            json.dumps(metadata),
            alias
            + (
                self.name,
                '__Metadata',
            )
            if alias
            else None,
        )
        for child in self.get_children():
            child.dump(fs_handler.join_path(base_path, self.eid), fs_handler, alias + (self.name,) if alias else None)