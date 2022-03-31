from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from signals_notebook.types import MID


class Material(BaseModel):
    asset_type_id: str = Field(alias='assetTypeId', allow_mutation=False)
    eid: MID = Field(allow_mutation=False)
    library: str = Field(allow_mutation=False)
    digest: Optional[str] = Field(allow_mutation=False, default=None)
    name: str = Field(title='Name')
    description: Optional[str] = Field(title='Description', default=None)
    created_at: datetime = Field(alias='createdAt', allow_mutation=False)
    edited_at: datetime = Field(alias='editedAt', allow_mutation=False)

    class Config:
        validate_assignment = True

    def __str__(self) -> str:
        return f'<{self.__class__.__name__} eid={self.eid}>'

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'materials'
