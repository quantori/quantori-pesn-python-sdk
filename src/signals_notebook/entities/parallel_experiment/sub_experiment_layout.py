import logging
from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities.contentful_entity import ContentfulEntity

log = logging.getLogger(__name__)


class SubExperimentLayout(ContentfulEntity):
    type: Literal[EntityType.SUB_EXPERIMENT_LAYOUT] = Field(allow_mutation=False)
    _template_name: ClassVar = 'subexp_layout.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.SUB_EXPERIMENT_LAYOUT

    def get_content(self) -> File:
        return super()._get_content(format='csv')
