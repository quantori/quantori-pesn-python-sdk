from enum import Enum
from typing import Generic, List, NewType, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl
from pydantic.generics import GenericModel

EntityClass = TypeVar('EntityClass')
AnyModel = TypeVar('AnyModel')


class ObjectType(str, Enum):
    ENTITY = 'entity'
    ADT_ROW = 'adtRow'
    COLUMN_DEFINITIONS = 'columnDefinitions'


class EntityType(str, Enum):
    NOTEBOOK = 'journal'
    EXPERIMENT = 'experiment'
    TEXT = 'text'
    CHEMICAL_DRAWING = 'chemicalDrawing'
    GRID = 'grid'
    ASSET = 'asset'
    BIO_SEQUENCE = 'bioSequence'


class EID(BaseModel):
    type: Union[EntityType, str]
    id: UUID

    def __init__(self, value: str):
        _type, _id = value.split(':')
        super().__init__(type=_type, id=_id)

    def __str__(self) -> str:
        return f'{self.type}:{self.id}'


class Links(BaseModel):
    self: HttpUrl
    first: Optional[HttpUrl] = None
    next: Optional[HttpUrl] = None
    prev: Optional[HttpUrl] = None


class ResponseData(GenericModel, Generic[EntityClass]):
    type: ObjectType
    eid: EID = Field(alias='id')
    links: Optional[Links] = None
    body: EntityClass = Field(alias='attributes')


class Response(GenericModel, Generic[EntityClass]):
    links: Links
    data: Union[ResponseData[EntityClass], List[ResponseData[EntityClass]]]


class DataObject(GenericModel, Generic[AnyModel]):
    data: AnyModel


class DataList(GenericModel, Generic[AnyModel]):
    data: List[AnyModel]


class EntityCreationRequestPayload(DataObject[AnyModel], Generic[AnyModel]):
    pass


class EntityShortDescription(BaseModel):
    type: Union[EntityType, str]
    id: EID


class Template(DataObject[EntityShortDescription]):
    pass


class Ancestors(DataList[EntityShortDescription]):
    pass


class File(BaseModel):
    name: str
    content: bytes
    content_type: str
