from enum import Enum
from typing import Generic, NewType, Optional, TypeVar, Union

from pydantic import BaseModel, Field, HttpUrl
from pydantic.generics import GenericModel

EID = NewType('EID', str)
EntityClass = TypeVar('EntityClass')


class EntityType(str, Enum):
    ENTITY = 'entity'


class Links(BaseModel):
    self: HttpUrl
    first: Optional[HttpUrl] = None
    next: Optional[HttpUrl] = None


class ResponseData(GenericModel, Generic[EntityClass]):
    type: EntityType
    eid: EID = Field(alias='id')
    links: Links
    body: EntityClass = Field(alias='attributes')


class Response(GenericModel, Generic[EntityClass]):
    links: Links
    data: Union[ResponseData[EntityClass], list[ResponseData[EntityClass]]]
