from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.jinja_env import env


class SamplesContainer(ContentfulEntity):
    type: Literal[EntityType.SAMPLES_CONTAINER] = Field(allow_mutation=False)
    _template_name: ClassVar = 'samplesContainer.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.WORD

    def get_content(self) -> File:
        return super()._get_content()

    def get_html(self) -> str:
        file = self._get_content()
        content = file.content.decode('utf-8')
        splited_content = content.split('\r\n')
        table_head = splited_content.pop(0).split(',')
        rows = []
        for elem in splited_content:
            if len(elem) == 0:
                continue
            rows.append(elem.split(','))

        template = env.get_template(self._template_name)
        return template.render(name=self.name, table_head=table_head, rows=rows)
