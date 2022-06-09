import csv
from io import StringIO
from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType
from signals_notebook.entities.samples.sample_tables_base import SamplesTableBase
from signals_notebook.jinja_env import env


class SamplesContainer(SamplesTableBase):
    type: Literal[EntityType.SAMPLES_CONTAINER] = Field(allow_mutation=False)
    _template_name: ClassVar = 'samplesContainer.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.SAMPLES_CONTAINER

    def get_html(self) -> str:
        file = self._get_content()
        content = StringIO(file.content.decode('utf-8'))
        csv_data = list(csv.reader(content))
        table_head = csv_data[0]
        rows = csv_data[1:]
        template = env.get_template(self._template_name)
        return template.render(name=self.name, table_head=table_head, rows=rows)
