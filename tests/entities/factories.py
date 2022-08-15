import factory

from signals_notebook.common_types import EID, EntityType
from signals_notebook.entities import (
    AdminDefinedObject,
    BiologicalSequence,
    ChemicalDrawing,
    Entity,
    Excel,
    Experiment,
    Image,
    MaterialsTable,
    Notebook,
    PowerPoint,
    Spotfire,
    Text,
    UploadedResource,
    Word,
)
from signals_notebook.entities.admin_defined_object import AdoType, CUSTOM_SYSTEM_OBJECT


class EIDFactory(factory.Factory):
    class Meta:
        model = EID

    id = factory.Faker('uuid4')
    type = factory.Iterator(EntityType)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        _id = kwargs.get('id')
        _type = kwargs.get('type')
        return model_class(f'{_type}:{_id}')


class EntityFactory(factory.Factory):
    class Meta:
        model = Entity

    eid = factory.SubFactory(EIDFactory)
    type = factory.Faker('word')
    name = factory.Faker('word')
    description = factory.Faker('text')
    digest = factory.Sequence(lambda n: f'{n}')
    created_at = factory.Faker('date_time')
    edited_at = factory.Faker('date_time')


class NotebookFactory(EntityFactory):
    class Meta:
        model = Notebook

    type = EntityType.NOTEBOOK


class ExperimentFactory(EntityFactory):
    class Meta:
        model = Experiment

    type = EntityType.EXPERIMENT


class TextFactory(EntityFactory):
    class Meta:
        model = Text

    type = EntityType.TEXT


class ChemicalDrawingFactory(EntityFactory):
    class Meta:
        model = ChemicalDrawing

    type = EntityType.CHEMICAL_DRAWING


class ImageFactory(EntityFactory):
    class Meta:
        model = Image

    type = EntityType.IMAGE_RESOURCE


class WordFactory(EntityFactory):
    class Meta:
        model = Word

    type = EntityType.WORD


class ExcelFactory(EntityFactory):
    class Meta:
        model = Excel

    type = EntityType.EXCEL


class BiologicalSequenceFactory(EntityFactory):
    class Meta:
        model = BiologicalSequence

    type = EntityType.BIO_SEQUENCE


class PowerPointFactory(EntityFactory):
    class Meta:
        model = PowerPoint

    type = EntityType.POWER_POINT


class SpotfireFactory(EntityFactory):
    class Meta:
        model = Spotfire

    type = EntityType.SPOTFIRE


class UploadedResourceFactory(EntityFactory):
    class Meta:
        model = UploadedResource

    type = EntityType.UPLOADED_RESOURCE


class MaterialTableFactory(EntityFactory):
    class Meta:
        model = MaterialsTable

    type = EntityType.MATERIAL_TABLE


class AdoTypeFactory(factory.Factory):
    class Meta:
        model = AdoType

    id = factory.Sequence(lambda n: f'{n}')
    base_type = 'experiment'
    ado_name = CUSTOM_SYSTEM_OBJECT


class AdminDefinedObjectFactory(EntityFactory):
    class Meta:
        model = AdminDefinedObject

    type = EntityType.ADO
    ado = factory.SubFactory(AdoTypeFactory)
