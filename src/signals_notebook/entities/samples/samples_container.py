from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType
from signals_notebook.entities.samples.sample_tables_base import SamplesTableBase


class SamplesContainer(SamplesTableBase):
    type: Literal[EntityType.SAMPLES_CONTAINER] = Field(allow_mutation=False)
    _template_name: ClassVar = 'samplesContainer.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.SAMPLES_CONTAINER
