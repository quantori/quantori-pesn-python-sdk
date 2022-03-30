import abc
from datetime import datetime
from typing import cast, Optional

from pydantic import BaseModel, Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.types import MaterialType, MID, Response, ResponseData


class Material(BaseModel, abc.ABC):
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
    @abc.abstractmethod
    def _get_material_type(cls) -> MaterialType:
        pass

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'materials'

    @classmethod
    def _get(cls, eid: MID) -> 'Material':
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), eid),
        )

        result = Response[cls](**response.json())  # type: ignore

        return cast(ResponseData, result.data).body
