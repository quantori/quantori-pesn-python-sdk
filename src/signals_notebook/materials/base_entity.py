from datetime import datetime
from typing import Optional

from pydantic import Field

from signals_notebook.base import PatchedModel
from signals_notebook.common_types import MID


class BaseMaterialEntity(PatchedModel):
    asset_type_id: str = Field(alias='assetTypeId', allow_mutation=False)
    eid: MID = Field(allow_mutation=False)
    library_name: str = Field(allow_mutation=False, alias='library')
    digest: Optional[str] = Field(allow_mutation=False, default=None)
    name: str = Field(title='Name', allow_mutation=False)
    created_at: datetime = Field(alias='createdAt', allow_mutation=False)
    edited_at: datetime = Field(alias='editedAt', allow_mutation=False)

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True

    def __str__(self) -> str:
        return f'<{self.__class__.__name__} eid={self.eid}>'

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'materials'
