import factory

from signals_notebook.common_types import EID, EntityType
from signals_notebook.entities import ChemicalDrawing, Entity, Experiment, Image, Notebook, Text


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
