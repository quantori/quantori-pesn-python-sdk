import re
from enum import Enum
from typing import Any, Generic, List, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, validator
from pydantic.generics import GenericModel

from signals_notebook.exceptions import EIDError

EntityClass = TypeVar('EntityClass')
AnyModel = TypeVar('AnyModel')


class ChemicalDrawingFormat(str, Enum):
    CDXML = 'cdxml'
    SVG = 'svg'
    MOL = 'mol'
    MOL3000 = 'mol-v3000'
    SMILES = 'smiles'


class ObjectType(str, Enum):
    ENTITY = 'entity'
    ADT_ROW = 'adtRow'
    COLUMN_DEFINITIONS = 'columnDefinitions'
    MATERIAL = 'material'
    ASSET_TYPE = 'assetType'


class EntityType(str, Enum):
    NOTEBOOK = 'journal'
    EXPERIMENT = 'experiment'
    TEXT = 'text'
    CHEMICAL_DRAWING = 'chemicalDrawing'
    GRID = 'grid'
    ASSET = 'asset'
    BIO_SEQUENCE = 'bioSequence'
    UPLOADED_RESOURCE = 'uploadedResource'
    IMAGE_RESOURCE = 'imageResource'


class MaterialType(str, Enum):
    LIBRARY = 'assetType'
    ASSET = 'asset'
    BATCH = 'batch'


class EID(str):
    """Entity ID"""

    def __new__(cls, content: Any, validate: bool = True):
        if validate:
            cls.validate(content)
        return str.__new__(cls, content)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any):
        if not isinstance(v, str):
            raise EIDError(value=v)

        try:
            _type, _id = v.split(':')
            UUID(_id)
        except ValueError:
            raise EIDError(value=v)

        return cls(v, validate=False)

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


class MID(str):
    """Material ID"""

    _id_pattern = re.compile('[0-9a-f]+', flags=re.IGNORECASE)

    def __new__(cls, content: Any, validate: bool = True):
        if validate:
            cls.validate(content)
        return str.__new__(cls, content)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any):
        if not isinstance(v, str):
            raise EIDError(value=v)

        try:
            _type, _id = v.split(':')
            MaterialType(_type)
        except ValueError:
            raise EIDError(value=v)

        if not cls._id_pattern.fullmatch(_id):
            raise EIDError(value=v)

        return cls(v, validate=False)

    @property
    def type(self) -> Union[MaterialType, str]:
        _type, _ = self.split(':')
        return MaterialType(_type)

    @property
    def id(self) -> str:
        _, _id = self.split(':')
        return _id


class Links(BaseModel):
    self: HttpUrl
    first: Optional[HttpUrl] = None
    next: Optional[HttpUrl] = None
    prev: Optional[HttpUrl] = None

    @validator('*', pre=True)
    def escape_spaces(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.replace(' ', '%20')

        return v


class ResponseData(GenericModel, Generic[EntityClass]):
    type: ObjectType
    eid: Union[EID, MID, UUID, str] = Field(alias='id')
    links: Optional[Links] = None
    body: EntityClass = Field(alias='attributes')


class Response(GenericModel, Generic[EntityClass]):
    links: Optional[Links] = None
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
