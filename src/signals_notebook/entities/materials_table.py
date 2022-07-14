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

    @classmethod
    def create(
        cls,
        *,
        container: Container,
        name: str,
        content: bytes = b'',
        file_extension: str = '',
        force: bool = True,
    ) -> Entity:
        file_extension = file_extension.replace('.', '')
        content_type = 'application/json'
        return container.add_child(
            name=name,
            content=content,
            content_type=content_type,
            force=force,
        )

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


#
# {
#     "type": "materialsTable",
#     "name": "Materials Table{*}",
#     "flags": {"isTemplate": false, "isSystem": false},
#     "layout": "{\"id\":\"4b6cb8d3-fb25-4d4f-95de-25ff8c600766\"}",
#     "ancestors": [
#         {
#             "type": "journal",
#             "eid": "journal:4deff948-163e-4e75-bbb2-b9f219eace5e",
#             "name": "Example notebook created by SDK",
#             "digest": "16635134",
#             "fields": {
#                 "Description": "Delete if you see this in UI",
#                 "My Notebook Field 1 (SK)": "",
#                 "My Notebook Field 2 (SK)": "",
#                 "Name": "Example notebook created by SDK",
#             },
#             "flags": {},
#         },
#         {
#             "eid": "experiment:1cf65229-dea3-4bdb-b6c5-daf8565e39a0",
#             "name": "TEST SDK",
#             "type": "experiment",
#             "digest": "86256909",
#         },
#     ],
# }
