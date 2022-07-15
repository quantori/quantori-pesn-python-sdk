import logging
import mimetypes
from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.jinja_env import env

log = logging.getLogger(__name__)


class MaterialsTable(ContentfulEntity):
    type: Literal[EntityType.MATERIAL_TABLE] = Field(allow_mutation=False)
    # _template_name: ClassVar = 'bio_sequence.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.MATERIAL_TABLE


    def get_content(self) -> File:
        return super()._get_content()
    #
    # def get_html(self) -> str:
    #     data = {'name': self.name}
    #     file = self.get_content()
    #     data['bio_sequence'] = 'data:{};base64,{}'.format(file.content_type, file.base64.decode('ascii'))
    #
    #     template = env.get_template(self._template_name)
    #     log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)
    #
    #     return template.render(data=data)
