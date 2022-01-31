import json
from typing import Any, cast, Dict, List

from pydantic import BaseModel, Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.types import EID, EntityClass, EntitySubtype, Request, RequestData, ResponseData


class Entity(BaseModel):
    eid: EID = Field(allow_mutation=False)

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
            target_class=cls,
        )

        return cast(ResponseData, response.data).body

    @classmethod
    def get_list(cls) -> List[EntityClass]:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(cls.get_endpoint(),),
            params=cls.get_list_params(),
            target_class=cls,
        )

        return [cast(ResponseData, item).body for item in response.data]

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
    def create(
        cls, *, digest: str = None, force: bool = True, attributes: Dict[str, Any] = None, **kwargs
    ) -> EntityClass:
        api = SignalsNotebookApi.get_default_api()

        if not attributes:
            attributes = {}

        request = Request(data=RequestData(type=cls.get_subtype(), attributes=attributes))
        response = api.call(
            method='POST',
            path=(cls.get_endpoint(),),
            params={
                'digest': digest,
                'force': json.dumps(force),
            },
            data=request.dict(),
            target_class=cls,
        )

        return cast(ResponseData, response.data).body

    def refresh(self) -> None:
        pass

    def save(self) -> None:
        pass
