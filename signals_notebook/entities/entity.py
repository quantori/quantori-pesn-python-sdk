import json
from typing import Any, cast, Dict, List, Optional

from pydantic import BaseModel, Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.types import (
    EntityCreationRequestPayload, EID, EntityClass, EntityShortDescription, EntitySubtype, Response,
    ResponseData,
)


class Entity(BaseModel):
    eid: EID = Field(allow_mutation=False)
    digest: Optional[str] = Field(allow_mutation=False, default=None)

    class Config:
        validate_assignment = True

    @classmethod
    def get_subtype(cls) -> EntitySubtype:
        raise NotImplementedError

    @classmethod
    def get_endpoint(cls) -> str:
        return 'entities'

    def delete(self) -> None:
        self.delete_by_id(self.eid)

    @classmethod
    def get_list_params(cls) -> Dict[str, Any]:
        return {
            'includeTypes': cls.get_subtype(),
        }

    @classmethod
    def get(cls, eid: EID) -> EntityClass:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(cls.get_endpoint(), eid),
        )

        result = Response[cls](**response.json())  # type: ignore

        return cast(ResponseData, result.data).body

    @classmethod
    def get_list(cls) -> List[EntityClass]:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(cls.get_endpoint(),),
            params=cls.get_list_params(),
        )

        result = Response[cls](**response.json())  # type: ignore

        return [cast(ResponseData, item).body for item in result.data]

    @classmethod
    def delete_by_id(cls, eid: EID, digest: str = None, force: bool = True) -> None:
        api = SignalsNotebookApi.get_default_api()

        api.call(
            method='DELETE',
            path=(cls.get_endpoint(), eid),
            params={
                'digest': digest,
                'force': json.dumps(force),
            },
        )

    @classmethod
    def _create(cls, *, digest: str = None, force: bool = True, request: EntityCreationRequestPayload) -> EntityClass:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='POST',
            path=(cls.get_endpoint(),),
            params={
                'digest': digest,
                'force': json.dumps(force),
            },
            data=request.dict(exclude_none=True),
        )

        result = Response[cls](**response.json())  # type: ignore

        return cast(ResponseData, result.data).body

    def refresh(self) -> None:
        pass

    def save(self, force: bool = True) -> None:
        api = SignalsNotebookApi.get_default_api()

        request_body = []
        for field in self.__fields__.values():
            if field.field_info.allow_mutation:
                request_body.append(
                    {'attributes': {'name': field.field_info.title, 'value': getattr(self, field.name)}}
                )

        api.call(
            method='PATCH',
            path=(self.get_endpoint(), self.eid, 'properties'),
            params={
                'digest': None if force else self.digest,
                'force': json.dumps(force),
            },
            data={
                'data': request_body,
            },
        )

    @property
    def short_description(self) -> EntityShortDescription:
        return EntityShortDescription(type=self.get_subtype(), id=self.eid)
