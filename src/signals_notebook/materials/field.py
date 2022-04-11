from enum import Enum
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from signals_notebook.attributes import Attribute
from signals_notebook.common_types import AttrID


class CollectionType(str, Enum):
    LIST = 'LIST'
    MULTI_SELECT = 'MULTI_SELECT'


class MaterialFieldType(str, Enum):
    ATTACHED_FILE = 'ATTACHED_FILE'
    ATTRIBUTE = 'ATTRIBUTE'
    BOOLEAN = 'BOOLEAN'
    CHEMICAL_DRAWING = 'CHEMICAL_DRAWING'
    DATETIME = 'DATETIME'
    DECIMAL = 'DECIMAL'
    EXTERNAL_LINK = 'EXTERNAL_LINK'
    LINK = 'LINK'
    MOLECULAR_FORMULA = 'MOLECULAR_FORMULA'
    MOLECULAR_MASS = 'MOLECULAR_MASS'
    TEMPERATURE = 'TEMPERATURE'
    TEXT = 'TEXT'
    CAS_NUMBER = 'CAS_NUMBER'
    DENSITY = 'DENSITY'
    SEQUENCE = 'SEQUENCE'
    INTEGER = 'INTEGER'


class BaseField(BaseModel):
    id: str
    name: str
    mandatory: bool
    hidden: bool
    calculated: bool = Field(default=False)
    read_only: bool = Field(alias='readOnly', default=False)
    data_type: Union[MaterialFieldType, str] = Field(alias='dataType')
    defined_by: str = Field(alias='definedBy')


class TextField(BaseField):
    data_type: Literal[MaterialFieldType.TEXT] = Field(alias='dataType')
    collection: Optional[CollectionType] = Field(default=None)
    options: Optional[List[str]] = Field(default=None)


class ChemicalDrawingField(BaseField):
    data_type: Literal[MaterialFieldType.CHEMICAL_DRAWING] = Field(alias='dataType')


class MolecularMassField(BaseField):
    data_type: Literal[MaterialFieldType.MOLECULAR_MASS] = Field(alias='dataType')


class DecimalField(BaseField):
    data_type: Literal[MaterialFieldType.DECIMAL] = Field(alias='dataType')


class IntegerField(BaseField):
    data_type: Literal[MaterialFieldType.INTEGER] = Field(alias='dataType')


class BooleanField(BaseField):
    data_type: Literal[MaterialFieldType.BOOLEAN] = Field(alias='dataType')


class MolecularFormulaField(BaseField):
    data_type: Literal[MaterialFieldType.MOLECULAR_FORMULA] = Field(alias='dataType')


class CASNumberField(BaseField):
    data_type: Literal[MaterialFieldType.CAS_NUMBER] = Field(alias='dataType')


class DensityField(BaseField):
    data_type: Literal[MaterialFieldType.DENSITY] = Field(alias='dataType')


class AttachedFileField(BaseField):
    data_type: Literal[MaterialFieldType.ATTACHED_FILE] = Field(alias='dataType')


class SequenceField(BaseField):
    data_type: Literal[MaterialFieldType.SEQUENCE] = Field(alias='dataType')


class TemperatureField(BaseField):
    data_type: Literal[MaterialFieldType.TEMPERATURE] = Field(alias='dataType')


class LinkField(BaseField):
    data_type: Literal[MaterialFieldType.LINK] = Field(alias='dataType')


class AttributeField(BaseField):
    data_type: Literal[MaterialFieldType.ATTRIBUTE] = Field(alias='dataType')
    multi_select: bool = Field(alias='multiSelect', default=False)
    attribute_id: AttrID = Field(alias='attribute')

    @property
    def attribute(self) -> Attribute:
        return Attribute.get(self.attribute_id)


GenericField = Union[
    Annotated[
        Union[
            AttachedFileField,
            AttributeField,
            BooleanField,
            CASNumberField,
            ChemicalDrawingField,
            DecimalField,
            DensityField,
            IntegerField,
            LinkField,
            MolecularFormulaField,
            MolecularMassField,
            SequenceField,
            TemperatureField,
            TextField,
        ],
        Field(discriminator='data_type'),
    ],
    BaseField,
]
