from datetime import datetime, timedelta

import factory

from signals_notebook.entities.notebook import Notebook
from signals_notebook.types import EntitySubtype


class NotebookFactory(factory.Factory):
    class Meta:
        model = Notebook
        exclude = ('uuid', )

    uuid = factory.Faker('uuid4')
    eid = factory.LazyAttribute(lambda o: f'{EntitySubtype.NOTEBOOK}{o.uuid}')
    name = factory.Faker('word')
    description = factory.Faker('text')
    digest = factory.Sequence(lambda n: f'{n}')
    createdAt = factory.Faker('date_time')
    editedAt = factory.Faker('date_time')


