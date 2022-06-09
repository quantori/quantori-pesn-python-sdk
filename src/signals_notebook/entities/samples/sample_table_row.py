from typing import Any, Dict, Literal

from pydantic import BaseModel, Field, validator

from signals_notebook.common_types import EID, ObjectType
from signals_notebook.entities.samples.sample import SampleProperty


class SampleTableRow(BaseModel):
    type: Literal[ObjectType.SAMPLES_TABLE_ROW] = Field(allow_mutation=False, default=ObjectType.SAMPLES_TABLE_ROW)
    eid: EID
    columns: Dict[str, SampleProperty]

    class Config:
        validate_assignment = True

    @validator('columns', pre=True)
    def set_columns(cls, values) -> Dict[str, SampleProperty]:
        return {key: SampleProperty(**value) for key, value in values.items()}

    @property
    def representation_for_update(self) -> Dict[str, Any]:
        return {
            'type': self.type,
            'attributes': {'columns': {key: value.dict() for key, value in self.columns.items()}},
        }
