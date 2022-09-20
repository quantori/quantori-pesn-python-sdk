import json
import logging
from functools import cached_property
from typing import Any, cast, Generator, Literal, Optional

from pydantic import BaseModel, Field

from signals_notebook.common_types import (
    Ancestors,
    EntityCreationRequestPayload,
    EntityType,
    Template,
)
from signals_notebook.entities import Entity
from signals_notebook.entities.chemical_drawing import (
    ChemicalDrawing,
    ChemicalDrawingPosition,
    ChemicalStructure,
    Structure,
)
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

    @staticmethod
    def _add_structures_from_metadata(
        metadata: list[dict[str, str]],
        chemical_structure: ChemicalStructure,
        position: ChemicalDrawingPosition,
        chemical_drawing: ChemicalDrawing,
    ) -> None:
        for metadata_structure in metadata:
            structure = Structure(
                id=metadata_structure['id'],
                type=chemical_structure,
                inchi=metadata_structure['inchi'],
                cdxml=metadata_structure['cdxml'],
            )
            chemical_drawing.add_structures(structure=structure, positions=position)

    @classmethod
    def load(cls, path: str, fs_handler: FSHandler, parallel_experiment: ParallelExperiment) -> None:
        cls._load(path, fs_handler, parallel_experiment)

    @classmethod
    def _load(cls, path: str, fs_handler: FSHandler, parent: Any) -> None:
        from signals_notebook.item_mapper import ItemMapper

        metadata = json.loads(fs_handler.read(fs_handler.join_path(path, 'metadata.json')))
        sub_experiment = cls.create(
            parallel_experiment=parent, description=metadata['description'], force=True
        )
        existing_chemical_drawing = [
            cast(ChemicalDrawing, i) for i in sub_experiment.get_children() if i.type == EntityType.CHEMICAL_DRAWING
        ][0]

        child_entities_folders = fs_handler.list_subfolders(path)
        for child_entity in child_entities_folders:
            child_path = fs_handler.join_path(path, child_entity)
            metadata = json.loads(fs_handler.read(fs_handler.join_path(child_path, 'metadata.json')))
            child_entity_type = child_entity.split(':')[0]
            entity_type = ItemMapper.get_item_class(child_entity_type)

            if child_entity_type == EntityType.CHEMICAL_DRAWING:

                if not metadata.get('reactants') or not metadata.get('products'):
                    continue
                cls._add_structures_from_metadata(
                    metadata['reactants'],
                    ChemicalStructure.REACTANT,
                    ChemicalDrawingPosition.REACTANTS,
                    existing_chemical_drawing,
                )
                cls._add_structures_from_metadata(
                    metadata['products'],
                    ChemicalStructure.PRODUCT,
                    ChemicalDrawingPosition.PRODUCTS,
                    existing_chemical_drawing,
                )
                cls._add_structures_from_metadata(
                    metadata['reagents'],
                    ChemicalStructure.REAGENT,
                    ChemicalDrawingPosition.REAGENTS,
                    existing_chemical_drawing,
                )

            else:
                entity_type._load(fs_handler.join_path(path, child_entity), fs_handler, sub_experiment)
