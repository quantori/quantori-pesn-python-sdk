from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.jinja_env import env


class Text(ContentfulEntity):
    type: Literal[EntityType.TEXT] = Field(allow_mutation=False)
    _template_name: ClassVar = 'text.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.TEXT

    @classmethod
    def create(cls, *, container: Container, name: str, content: str = '', force: bool = True) -> Entity:
        return container.add_child(
            name=name,
            content=content.encode('utf-8'),
            content_type='text/plain',
            force=force,
        )

    def get_content(self) -> File:
        return super()._get_content()

    def get_html(self) -> str:
        file = self._get_content()
        data = {'name': self.name, 'content': file.content.decode('utf-8')}
        template = env.get_template(self._template_name)

        return template.render(data=data)
