import logging
from functools import cached_property
from typing import ClassVar, Literal, Optional, Union

from pydantic import Field

from signals_notebook.common_types import ChemicalDrawingFormat, EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.entities.stoichiometry.stoichiometry import Stoichiometry
from signals_notebook.jinja_env import env

log = logging.getLogger(__name__)


class ChemicalDrawing(ContentfulEntity):
    type: Literal[EntityType.CHEMICAL_DRAWING] = Field(allow_mutation=False)
    _template_name: ClassVar = 'chemical_drawing.html'

    class Config:
        keep_untouched = (cached_property,)

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.CHEMICAL_DRAWING

    @classmethod
    def create(
        cls,
        *,
        container: Container,
        name: str,
        content_type: str,
        content: bytes = b'',
        force: bool = True,
    ) -> Entity:
        log.debug('Create entity: %s with name: %s in Container: %s', cls.eid, name, container.eid)
        return container.add_child(
            name=name,
            content=content,
            content_type=content_type,
            force=force,
        )

    def get_content(self, format: Optional[ChemicalDrawingFormat] = None) -> File:
        return super()._get_content(format=format)

    @cached_property
    def stoichiometry(self) -> Union[Stoichiometry, list[Stoichiometry]]:
        return Stoichiometry.fetch_data(self.eid)

    def get_html(self) -> str:
        data = {'name': self.name, 'stoichiometry': {}}
        file = self.get_content(format=ChemicalDrawingFormat.SVG)
        data['svg'] = 'data:{};base64,{}'.format(file.content_type, file.base64.decode('ascii'))
        if isinstance(self.stoichiometry, Stoichiometry):
            data['stoichiometry_html'] = self.stoichiometry.get_html()

        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(data=data)
