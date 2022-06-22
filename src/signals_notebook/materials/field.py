import logging
from enum import Enum
from typing import Annotated, Any, List, Literal, Optional, TYPE_CHECKING, Union

from pydantic import BaseModel, Field

from signals_notebook.attributes import Attribute
from signals_notebook.common_types import AttrID, File

if TYPE_CHECKING:
    from signals_notebook.materials.material import Material

log = logging.getLogger(__name__)


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
    defined_by: str = Field(alias='definedBy', default='SYSTEM_DEFAULT')

    def to_internal_value(self, value: Any) -> Any:
        return value

    def to_representation(self, value: Any, material: 'Material', **kwargs) -> Any:
        return value


class TextFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.TEXT] = Field(alias='dataType', default=MaterialFieldType.TEXT)
    collection: Optional[CollectionType] = Field(default=None)
    options: Optional[List[str]] = Field(default=None)


class ChemicalDrawingFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.CHEMICAL_DRAWING] = Field(
        alias='dataType', default=MaterialFieldType.CHEMICAL_DRAWING
    )


class MolecularMassFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.MOLECULAR_MASS] = Field(
        alias='dataType', default=MaterialFieldType.MOLECULAR_MASS
    )


class DecimalFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.DECIMAL] = Field(alias='dataType', default=MaterialFieldType.DECIMAL)


class IntegerFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.INTEGER] = Field(alias='dataType', default=MaterialFieldType.INTEGER)


class BooleanFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.BOOLEAN] = Field(alias='dataType', default=MaterialFieldType.BOOLEAN)


class MolecularFormulaFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.MOLECULAR_FORMULA] = Field(
        alias='dataType', default=MaterialFieldType.MOLECULAR_FORMULA
    )


class CASNumberFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.CAS_NUMBER] = Field(alias='dataType', default=MaterialFieldType.CAS_NUMBER)


class DensityFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.DENSITY] = Field(alias='dataType', default=MaterialFieldType.DENSITY)


class AttachedFileFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.ATTACHED_FILE] = Field(
        alias='dataType', default=MaterialFieldType.ATTACHED_FILE
    )

    def to_representation(self, value: Any, material: 'Material', **kwargs) -> Any:
        """Get Material field attachment

        Args:
            value: field value
            material: material
            **kwargs:

        Returns:
            One of the Materials
        """
        return material.get_attachment(self.id)

    def to_internal_value(self, value: Any) -> Any:
        """Get field value as dictionary

        Args:
            value: field value

        Returns:
            field value as dictionary
        """
        if not isinstance(value, File):
            log.exception('File expected')
            raise TypeError('File expected')

        return {'filename': value.name, 'base64': value.base64.decode('utf-8')}


class SequenceFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.SEQUENCE] = Field(alias='dataType', default=MaterialFieldType.SEQUENCE)


class TemperatureFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.TEMPERATURE] = Field(alias='dataType', default=MaterialFieldType.TEMPERATURE)


class LinkFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.LINK] = Field(alias='dataType', default=MaterialFieldType.LINK)

    def to_representation(self, value: Any, material: 'Material', **kwargs) -> Any:
        """Get Entity by value id

        Args:
            value: field value
            material: material
            **kwargs:

        Returns:
            One of the Entities
        """
        if not value:
            return None

        from signals_notebook.entities.entity_store import EntityStore

        return EntityStore.get(value['eid'])

    def to_internal_value(self, value: Any) -> Any:
        """Get field value as dictionary

        Args:
            value: field value

        Returns:
            field value as dictionary
        """
        from signals_notebook.entities.entity import Entity

        if not isinstance(value, Entity):
            log.exception('Entity expected')
            raise TypeError('Entity expected')

        return {'eid': value.eid, 'name': value.name, 'type': value.type}


class AttributeFieldDefinition(BaseFieldDefinition):
    data_type: Literal[MaterialFieldType.ATTRIBUTE] = Field(alias='dataType', default=MaterialFieldType.ATTRIBUTE)
    multi_select: bool = Field(alias='multiSelect', default=False)
    attribute_id: AttrID = Field(alias='attribute')

    @property
    def attribute(self) -> Attribute:
        """Get Attribute object by id

        Returns:
            Attribute
        """
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
        allow_population_by_field_name = True


class BatchConfig(BaseModel):
    numbering: Numbering
    fields: List[GenericFieldDefinition]
    display_name: str = Field(alias='displayName')

    class Config:
        frozen = True
        allow_population_by_field_name = True


class MaterialField(BaseModel):
    is_changed: bool = False
    definition: GenericFieldDefinition = Field(allow_mutation=False)
    value: Any

    class Config:
        validate_assignment = True


class FieldContainer:
    def __init__(self, material: 'Material', field_definitions: List[GenericFieldDefinition], **data):
        self._data: dict[str, MaterialField] = {}
        self._material = material

        for field_definition in field_definitions:
            self._data[field_definition.name] = MaterialField.construct(
                definition=field_definition,
                value=data.get(field_definition.name, {}).get('value'),
                is_changed=False,
            )

    def items(self):
        """Get data items

        Returns:
            A view object that displays a list of data's (key, value) tuple pair.
        """
        return self._data.items()

    def __getitem__(self, key: str) -> Any:
        field = self._data[key]

        return field.definition.to_representation(field.value, self._material)

    def __setitem__(self, key: str, value: Any):
        if key not in self._data:
            raise KeyError()

        field = self._data[key]

        field.value = field.definition.to_internal_value(value)
        field.is_changed = True
