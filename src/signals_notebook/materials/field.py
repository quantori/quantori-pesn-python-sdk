from enum import Enum
from typing import Annotated, Any, List, Literal, Optional, Union

from pydantic import BaseModel, Field, validator

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
    SEQUENCE_FILE = 'SEQUENCE_FILE'
    INTEGER = 'INTEGER'


class BaseFieldDefinition(BaseModel):
    id: str
    name: str
    mandatory: bool
    hidden: bool
    calculated: bool = Field(default=False)
    read_only: bool = Field(alias='readOnly', default=False)
    data_type: Union[MaterialFieldType, str] = Field(alias='dataType')
    defined_by: str = Field(alias='definedBy')


class TextFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.TEXT] = Field(alias='dataType')
    collection: Optional[CollectionType] = Field(default=None)
    options: Optional[List[str]] = Field(default=None)


class ChemicalDrawingFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.CHEMICAL_DRAWING] = Field(alias='dataType')


class MolecularMassFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.MOLECULAR_MASS] = Field(alias='dataType')


class DecimalFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.DECIMAL] = Field(alias='dataType')


class IntegerFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.INTEGER] = Field(alias='dataType')


class BooleanFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.BOOLEAN] = Field(alias='dataType')


class MolecularFormulaFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.MOLECULAR_FORMULA] = Field(alias='dataType')


class CASNumberFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.CAS_NUMBER] = Field(alias='dataType')


class DensityFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.DENSITY] = Field(alias='dataType')


class AttachedFileFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.ATTACHED_FILE] = Field(alias='dataType')


class SequenceFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.SEQUENCE] = Field(alias='dataType')


class TemperatureFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.TEMPERATURE] = Field(alias='dataType')


class LinkFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.LINK] = Field(alias='dataType')


class AttributeFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.ATTRIBUTE] = Field(alias='dataType')
    multi_select: bool = Field(alias='multiSelect', default=False)
    attribute_id: AttrID = Field(alias='attribute')

    @property
    def attribute(self) -> Attribute:
        return Attribute.get(self.attribute_id)


GenericFieldDefinition = Union[
    Annotated[
        Union[
            AttachedFileFieldDefinition,
            AttributeFieldDefinition,
            BooleanFieldDefinition,
            CASNumberFieldDefinition,
            ChemicalDrawingFieldDefinition,
            DecimalFieldDefinition,
            DensityFieldDefinition,
            IntegerFieldDefinition,
            LinkFieldDefinition,
            MolecularFormulaFieldDefinition,
            MolecularMassFieldDefinition,
            SequenceFieldDefinition,
            TemperatureFieldDefinition,
            TextFieldDefinition,
        ],
        Field(discriminator='data_type'),
    ],
    BaseFieldDefinition,
]


class Numbering(BaseModel):
    format: str


class AssetConfig(BaseModel):
    numbering: Numbering
    fields: List[GenericFieldDefinition]
    display_name: str = Field(alias='displayName')
    asset_name_field_id: Optional[str] = Field(alias='assetNameFieldId', default=None)

    class Config:
        frozen = True


class BatchConfig(BaseModel):
    numbering: Numbering
    fields: List[GenericFieldDefinition]
    display_name: str = Field(alias='displayName')

    class Config:
        frozen = True


class Field(BaseModel):
    is_changed: bool = False
    field_definition: GenericFieldDefinition = Field(allow_mutation=False)
    value: Any

    class Config:
        validate_assignment = True

    @validator('value', always=True, pre=True)
    def validate_value(cls, value: Any, values, **kwargs):
        field_definition = values['field_definition']

        if (
            field_definition.mandatory
            and value is None
            and field_definition.data_type
            not in (
                MaterialFieldType.SEQUENCE,
                MaterialFieldType.CHEMICAL_DRAWING,
                MaterialFieldType.ATTACHED_FILE,
                MaterialFieldType.SEQUENCE_FILE,
            )
        ):
            raise ValueError('Value is mandatory')

        return value


class FieldContainer:
    _data: dict[str, Field] = {}

    def __init__(self, field_definitions: List[GenericFieldDefinition], **data):
        for field_definition in field_definitions:
            self._data[field_definition.name] = Field(
                field_definition=field_definition,
                value=data.get(field_definition.name, {}).get('value'),
                is_changed=False,
            )

    def items(self):
        return self._data.items()

    def __getitem__(self, key: str) -> Any:
        return self._data[key].value

    def __setitem__(self, key: str, value: Any):
        if key not in self._data:
            raise KeyError()

        self._data[key].value = value
        self._data[key].is_changed = True
