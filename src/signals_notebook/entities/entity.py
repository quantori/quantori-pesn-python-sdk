import json
from datetime import datetime
from typing import Any, cast, Dict, Generator, Optional, Type, TypeVar

from pydantic import BaseModel, Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.types import (
    EID,
    EntityClass,
    EntityCreationRequestPayload,
    EntityShortDescription,
    EntityType,
    Response,
    ResponseData,
)

ChildClass = TypeVar('ChildClass', bound='Entity')


class Entity(BaseModel):
    type: str = Field(allow_mutation=False)
    eid: EID = Field(allow_mutation=False)
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
    def _get_entity_type(cls) -> EntityType:
        raise NotImplementedError

    @classmethod
    def get_subclasses(cls) -> Generator[Type['Entity'], None, None]:
        for subclass in cls.__subclasses__():
            yield from subclass.get_subclasses()
            yield subclass

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'entities'

    @classmethod
    def _get_list_params(cls) -> Dict[str, Any]:
        return {
            'include_types': [cls._get_entity_type()],
        }

    @classmethod
    def get_list(cls) -> Generator['Entity', None, None]:
        from signals_notebook.entities.entity_store import EntityStore
        return EntityStore.get_list(**cls._get_list_params())

    def delete(self) -> None:
        from signals_notebook.entities.entity_store import EntityStore
        EntityStore.delete(self.eid)

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
        from signals_notebook.entities import EntityStore

        EntityStore.refresh(self)

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
