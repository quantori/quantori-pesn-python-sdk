from enum import Enum
from typing import Generic, List, NewType, Optional, TypeVar, Union

from pydantic import BaseModel, Field, HttpUrl
from pydantic.generics import GenericModel

EID = NewType('EID', str)
EntityClass = TypeVar('EntityClass')
AnyModel = TypeVar('AnyModel')


class EntityType(str, Enum):
    ENTITY = 'entity'
    ADT_ROW = 'adtRow'
    COLUMN_DEFINITIONS = 'columnDefinitions'


class EntitySubtype(str, Enum):
    NOTEBOOK = 'journal'
    EXPERIMENT = 'experiment'
    TEXT = 'text'
    CHEMICAL_DRAWING = 'chemicalDrawing'
    GRID = 'grid'


class Links(BaseModel):
    self: HttpUrl
    first: Optional[HttpUrl] = None
    next: Optional[HttpUrl] = None


class ResponseData(GenericModel, Generic[EntityClass]):
    type: EntityType
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
    type: Union[EntitySubtype, str]
    id: EID


class Template(DataObject[EntityShortDescription]):
    pass


class Ancestors(DataList[EntityShortDescription]):
    pass


class File(BaseModel):
    name: str
    content: bytes
    content_type: str
