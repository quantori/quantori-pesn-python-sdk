import logging
import mimetypes
import os
import re
from base64 import b64encode
from datetime import datetime
from enum import Enum
from typing import Any, Generic, List, Optional, TypeVar, Union
from uuid import UUID

from dateutil.parser import parse
from pydantic import BaseModel, Field, HttpUrl, validator
from pydantic.generics import GenericModel

from signals_notebook.exceptions import EIDError

EntityClass = TypeVar('EntityClass')
AnyModel = TypeVar('AnyModel')

log = logging.getLogger(__name__)


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
    ATTRIBUTE = 'attribute'
    STOICHIOMETRY = 'stoichiometry'
    PROPERTY = 'property'
    USER = 'user'
    PROFILE = 'profile'
    GROUP = 'group'
    ROLE = 'role'
    PLATE_ROW = 'plateRow'
    ATTRIBUTE_OPTION = 'option'
    CHOICE = 'choice'
    SUB_EXPERIMENT = 'subexpSummaryRow'
    CONTAINER = 'container'
    REACTION_PRODUCT = 'reactionProduct'
    REACTION_REACTANT = 'reactionReactant'
    REACTION_REAGENT = 'reactionReagent'


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
    WORD = 'viewonly'
    EXCEL = 'excel'
    SAMPLE = 'sample'
    SAMPLES_CONTAINER = 'samplesContainer'
    POWER_POINT = 'presentation'
    SPOTFIRE = 'spotfiredxp'
    TODO_LIST = 'linkedTaskContainer'
    TASK = 'task'
    PLATE_CONTAINER = 'plateContainer'
    MATERIAL_TABLE = 'materialsTable'
    PARALLEL_EXPERIMENT = 'paraexp'
    SUB_EXPERIMENT = 'parasubexp'
    SUB_EXPERIMENT_SUMMARY = 'paragrid'
    SUB_EXPERIMENT_LAYOUT = 'paraLayout'
    ADO = 'ado'
    REQUEST = 'request'
    TASK_CONTAINER = 'taskContainer'


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
        """Validate Entity ID

        Args:
            v: Entity ID

        Returns:
        """
        if not isinstance(v, str):
            log.error('%s is not instance of str', v)
            raise EIDError(value=v)

        try:
            _type, _id, *_ = v.split(':')
            UUID(_id)
        except ValueError:
            log.exception('Cannot get id and type from value')
            raise EIDError(value=v)

        return cls(v, validate=False)

    @property
    def type(self) -> Union[EntityType, str]:
        """Get entity type

        Returns:
            One of the entity types
        """
        _type, _id, *_ = self.split(':')
        try:
            return EntityType(_type)
        except ValueError:
            log.exception('Cannot get type: %s. There is no the same type in program', _type)
            return _type

    @property
    def id(self) -> UUID:
        """Get UUID

        Returns:
            UUID
        """
        _type, _id, *_ = self.split(':')
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
        """Validate Material ID

        Args:
            v: Material ID

        Returns:

        """
        if not isinstance(v, str):
            log.error('%s is not instance of str', v)
            raise EIDError(value=v)

        try:
            _type, _id = v.split(':')
            MaterialType(_type)
        except ValueError:
            log.exception('Cannot get id and type from value')
            raise EIDError(value=v)

        if not cls._id_pattern.fullmatch(_id):
            log.error('ID: %s is not the same with %s pattern', _id, cls._id_pattern)
            raise EIDError(value=v)

        return cls(v, validate=False)

    @property
    def type(self) -> MaterialType:
        """Get one of the material types

        Returns:
            MaterialType
        """
        _type, _ = self.split(':')
        return MaterialType(_type)

    @property
    def id(self) -> str:
        """Get id of material type

        Returns:
            str id
        """
        _, _id = self.split(':')
        return _id


class AttrID(str):
    """Attribute ID"""

    def __new__(cls, content: Any, validate: bool = True):
        if validate:
            cls.validate(content)
        return str.__new__(cls, content)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any):
        """Validate Attribute ID

        Args:
            v: Attribute ID

        Returns:

        """
        if not isinstance(v, str):
            log.error('%s is not instance of str', v)
            raise EIDError(value=v)

        try:
            _type, _id = v.split(':')
            int(_id)
        except ValueError:
            log.exception('Cannot get id and type from value')
            raise EIDError(value=v)

        if _type != ObjectType.ATTRIBUTE:
            log.error('Type: %s is not the same with %s', _type, ObjectType.ATTRIBUTE)
            raise EIDError(value=v)

        return cls(v, validate=False)

    @property
    def type(self) -> ObjectType:
        """Get one of the object types

        Returns:
            ObjectType
        """
        _type, _ = self.split(':')
        return ObjectType(_type)

    @property
    def id(self) -> int:
        """Get id of object type

        Returns:
            int id
        """
        _, _id = self.split(':')
        return int(_id)


class Links(BaseModel):
    self: HttpUrl
    first: Optional[HttpUrl] = None
    next: Optional[HttpUrl] = None
    prev: Optional[HttpUrl] = None

    @validator('*', pre=True)
    def escape_spaces(cls, v: Optional[str]) -> Optional[str]:
        """Replace all spaces

        Args:
            v: value

        Returns:
            value with replaced spaces
        """
        if v is not None:
            return v.replace(' ', '%20')

        return v


class ResponseData(GenericModel, Generic[EntityClass]):
    type: ObjectType
    eid: Union[EID, MID, AttrID, UUID, str] = Field(alias='id')
    links: Optional[Links] = None
    body: EntityClass = Field(alias='attributes')
    relationships: Optional[dict[str, Any]] = Field(default=None)
    meta: Optional[dict[str, Any]] = Field(default=None)

    def __init__(self, _context: dict[str, Any] = None, **kwargs):
        attributes = kwargs.get('attributes', {})

        if _context:
            attributes = {**attributes, **_context}

        super().__init__(**{**kwargs, 'attributes': attributes})


class Response(GenericModel, Generic[EntityClass]):
    links: Optional[Links] = None
    data: Union[ResponseData[EntityClass], List[ResponseData[EntityClass]]]

    def __init__(self, _context: dict[str, Any] = None, **kwargs):
        data = kwargs.get('data', {})

        if _context:
            if isinstance(data, list):
                data = [{'_context': _context, **item} for item in data]
            else:
                data = {'_context': _context, **data}

        super().__init__(**{**kwargs, 'data': data})


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

    def __init__(self, f=None, **kwargs):
        if f:
            name = os.path.basename(f.name)
            content = f.read()
            content_type, _ = mimetypes.guess_type(name)

            super().__init__(name=name, content=content, content_type=content_type)
        else:
            super().__init__(**kwargs)

    @property
    def size(self) -> int:
        """Get file size

        Returns:
            file size
        """
        return len(self.content)

    @property
    def base64(self) -> bytes:
        return b64encode(self.content)

    @classmethod
    def read(cls, file_name: str, mode='rb') -> 'File':
        """Read content of the file

        Args:
            file_name: file name in string format
            mode: specifies the mode in which the file is opened

        Returns:
            File
        """
        with open(file_name, mode) as f:
            return cls(f)

    def save(self, path: str) -> None:
        """Save content in file

        Args:
            path: path to the file

        Returns:

        """
        _path = path
        if os.path.isdir(path):
            _path = os.path.join(path, self.name)

        with open(_path, 'wb') as f:
            f.write(self.content)


class DateTime(datetime):
    @classmethod
    def __get_validators__(cls):
        yield cls._validate_date

    @staticmethod
    def _validate_date(value: Union[str, datetime]) -> datetime:
        if isinstance(value, datetime):
            return value

        return parse(value)
