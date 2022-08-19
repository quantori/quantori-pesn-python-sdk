import json
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
from signals_notebook.entities.chemical_drawing import ChemicalDrawingPosition, ChemicalStructure, Structure
from signals_notebook.entities.container import Container
from signals_notebook.entities.parallel_experiment.parallel_experiment import ParallelExperiment
from signals_notebook.jinja_env import env
from signals_notebook.utils.fs_handler import FSHandler

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

    @classmethod
    def load(cls, path: str, fs_handler: FSHandler, parallel_experiment: ParallelExperiment) -> None:
        from signals_notebook.item_mapper import ItemMapper

        metadata = json.loads(fs_handler.read(fs_handler.join_path(path, 'metadata.json')))
        sub_experiment = cls.create(
            parallel_experiment=parallel_experiment, description=metadata['description'], force=True
        )
        existing_chemical_drawing = [i for i in sub_experiment.get_children() if i.type == EntityType.CHEMICAL_DRAWING][
            0
        ]

        child_entities_folders = fs_handler.list_subfolders(path)
        for child_entity in child_entities_folders:
            child_path = fs_handler.join_path(path, child_entity)
            metadata = json.loads(fs_handler.read(fs_handler.join_path(child_path, 'metadata.json')))
            child_entity_type = child_entity.split(':')[0]
            entity_type = ItemMapper.get_item_class(child_entity_type)

            if child_entity_type == EntityType.CHEMICAL_DRAWING:

                if not metadata.get('reactants') or not metadata.get('products'):
                    continue

                for reactant in metadata['reactants']:
                    structure = Structure(
                        id=reactant['id'],
                        type=ChemicalStructure.REACTANT,
                        inchi=reactant['inchi'],
                        cdxml=reactant['cdxml'],
                    )
                    existing_chemical_drawing.add_structures(
                        structure=structure, positions=ChemicalDrawingPosition.REACTANTS
                    )
                for product in metadata['products']:
                    structure = Structure(
                        id=product['id'],
                        type=ChemicalStructure.PRODUCT,
                        inchi=product['inchi'],
                        cdxml=product['cdxml'],
                    )
                    existing_chemical_drawing.add_structures(
                        structure=structure, positions=ChemicalDrawingPosition.PRODUCTS
                    )
                for reagent in metadata['reagents']:
                    structure = Structure(
                        id=reagent['id'],
                        type=ChemicalStructure.REAGENT,
                        inchi=reagent['inchi'],
                        cdxml=reagent['cdxml'],
                    )
                    existing_chemical_drawing.add_structures(
                        structure=structure, positions=ChemicalDrawingPosition.REAGENTS
                    )

            else:
                entity_type.load(fs_handler.join_path(path, child_entity), fs_handler, sub_experiment)
