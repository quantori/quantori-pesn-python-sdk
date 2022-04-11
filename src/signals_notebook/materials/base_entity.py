from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from signals_notebook.base import PatchedModel
from signals_notebook.common_types import MID
from signals_notebook.materials.user import User

MaterialFieldValue = Union[str, List[str], User, Any]


class MaterialField(BaseModel):
    value: MaterialFieldValue


class BaseMaterialEntity(PatchedModel):
    asset_type_id: str = Field(alias='assetTypeId', allow_mutation=False)
    eid: MID = Field(allow_mutation=False)
    library_name: str = Field(allow_mutation=False, alias='library')
    digest: Optional[str] = Field(allow_mutation=False, default=None)
    name: str = Field(title='Name', allow_mutation=False)
    created_at: datetime = Field(alias='createdAt', allow_mutation=False)
    edited_at: datetime = Field(alias='editedAt', allow_mutation=False)
    fields: Dict[str, MaterialField] = Field(alias='fields', default={})

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True

    def __str__(self) -> str:
        return f'<{self.__class__.__name__} eid={self.eid}>'

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'materials'

    def __getitem__(self, index: str) -> MaterialFieldValue:
        return self.fields[index].value
