from enum import Enum
from typing import Generic, List, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl
from pydantic.generics import GenericModel

from signals_notebook.exceptions import EIDError

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


class EID(str):

    def __new__(cls, content):
        EID.validate(content)
        return str.__new__(cls, content)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: str):
        try:
            _type, _id = v.split(':')
            UUID(_id)
        except ValueError:
            raise EIDError()

        return v

    @property
    def type(self) -> Union[EntityType, str]:
        _type, _ = self.split(':')
        try:
            return EntityType(_type)
        except ValueError:
            return _type

    @property
    def id(self) -> UUID:
        _, _id = self.split(':')
        return UUID(_id)


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
