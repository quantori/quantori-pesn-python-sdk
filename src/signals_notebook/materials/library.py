from datetime import datetime
from typing import cast, List, Literal

from pydantic import BaseModel, Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.materials.material import Material
from signals_notebook.types import Links, MaterialType, MID, Response, ResponseData


class ChangeBlameRecord(BaseModel):
    links: Links


class ChangeRecord(BaseModel):
    at: datetime = Field(allow_mutation=False)
    by: ChangeBlameRecord = Field(allow_mutation=False)

    class Config:
        validate_assignment = True


class _LibraryListData(BaseModel):
    id: str = Field(allow_mutation=False)
    name: str = Field(title='Name')
    digest: str = Field(allow_mutation=False, default=None)
    edited: ChangeRecord = Field(allow_mutation=False)
    created: ChangeRecord = Field(allow_mutation=False)

    class Config:
        validate_assignment = True


class Library(Material):
    type: Literal[MaterialType.LIBRARY] = Field(allow_mutation=False, default=MaterialType.LIBRARY)

    class Config:
        validate_assignment = True

    @classmethod
    def get_list(cls) -> List['Library']:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), 'libraries'),
        )

        result = Response[_LibraryListData](**response.json())

        libraries: List['Library'] = []
        for item in result.data:
            data = cast(_LibraryListData, cast(ResponseData, item).body)
            libraries.append(
                cls(
                    assetTypeId=data.id,
                    eid=MID(f'{MaterialType.LIBRARY}:{data.id}'),
                    library=data.name,
                    name=data.name,
                    digest=data.digest.split(':')[0],
                    createdAt=data.created.at,
                    editedAt=data.edited.at,
                )
            )

        return libraries
