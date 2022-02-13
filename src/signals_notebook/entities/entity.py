import cgi
import json
import mimetypes
from datetime import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel, Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.types import (
    EntityCreationRequestPayload,
    EID,
    EntityClass,
    EntityShortDescription,
    EntitySubtype,
    File,
    Response,
    ResponseData,
)

ChildClass = TypeVar('ChildClass', bound='Entity')


class Entity(BaseModel):
    type: EntitySubtype
    eid: EID = Field(allow_mutation=False)
    digest: Optional[str] = Field(allow_mutation=False, default=None)
    name: str = Field(title='Name')
    description: Optional[str] = Field(title='Description', default=None)
    created_at: datetime = Field(alias='createdAt', allow_mutation=False)
    edited_at: datetime = Field(alias='editedAt', allow_mutation=False)

    class Config:
        validate_assignment = True

    @classmethod
    def _get_subtype(cls) -> EntitySubtype:
        raise NotImplementedError

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'entities'

    @classmethod
    def _get_list_params(cls) -> Dict[str, Any]:
        return {
            'includeTypes': cls._get_subtype(),
        }

    @classmethod
    def get(cls, eid: EID) -> EntityClass:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), eid),
        )

        result = Response[cls](**response.json())  # type: ignore

        return cast(ResponseData, result.data).body

    @classmethod
    def get_list(cls) -> List[EntityClass]:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(),),
            params=cls._get_list_params(),
        )

        result = Response[cls](**response.json())  # type: ignore

        return [cast(ResponseData, item).body for item in result.data]

    @classmethod
    def delete_by_id(cls, eid: EID, digest: str = None, force: bool = True) -> None:
        api = SignalsNotebookApi.get_default_api()

        api.call(
            method='DELETE',
            path=(cls._get_endpoint(), eid),
            params={
                'digest': digest,
                'force': json.dumps(force),
            },
        )

    def delete(self) -> None:
        self.delete_by_id(self.eid)

    @classmethod
    def _create(cls, *, digest: str = None, force: bool = True, request: EntityCreationRequestPayload) -> EntityClass:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='POST',
            path=(cls._get_endpoint(),),
            params={
                'digest': digest,
                'force': json.dumps(force),
            },
            json=request.dict(exclude_none=True),
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
            path=(self._get_endpoint(), self.eid, 'properties'),
            params={
                'digest': None if force else self.digest,
                'force': json.dumps(force),
            },
            json={
                'data': request_body,
            },
        )

    @property
    def short_description(self) -> EntityShortDescription:
        return EntityShortDescription(type=self.type, id=self.eid)

    def get_content(self, format: Optional[str] = None) -> File:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.eid, 'export'),
            params={
                'format': format,
            },
        )

        content_disposition = response.headers.get('content-disposition', '')
        _, params = cgi.parse_header(content_disposition)

        return File(
            name=params['filename'], content=response.content, content_type=response.headers.get('content-type')
        )

    def add_child(
        self,
        name: str,
        content: bytes,
        child_class: Type[ChildClass],
        content_type: str,
        force: bool = True,
    ) -> ChildClass:
        api = SignalsNotebookApi.get_default_api()

        extension = mimetypes.guess_extension(content_type)
        file_name = f'{name}{extension}'

        response = api.call(
            method='POST',
            path=(self._get_endpoint(), self.eid, 'children', file_name),
            params={
                'digest': None if force else self.digest,
                'force': json.dumps(force),
            },
            headers={
                'Content-Type': content_type,
            },
            data=content,
        )

        result = Response[child_class](**response.json())  # type: ignore

        return cast(ResponseData, result.data).body

    def get_children(self) -> List[ChildClass]:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.eid, 'children'),
        )

        entity_classes = (*Entity.__subclasses__(), Entity)

        result = Response[Union[entity_classes]](**response.json())  # type: ignore

        return [cast(ResponseData, item).body for item in result.data]
